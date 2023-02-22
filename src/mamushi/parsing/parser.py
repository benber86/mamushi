# EXPERIMENTAL VYPER PARSER
# https://github.com/vyperlang/vyper/
import re
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from lark import Lark, Token, Tree

from mamushi.parsing import tokens
from mamushi.parsing.indenter import PythonIndenter
from mamushi.parsing.pytree import Leaf, Node
from mamushi.parsing.tokens import NEWLINE

CommentMapping = Dict[Tuple[Any, ...], Token]
StandAloneCommentMapping = Dict[Tuple[Any, ...], List[Token]]
DedentCount = Dict[Tuple[Any, ...], int]


class Parser(object):
    """
    Parse a vyper file using lark, converts the lark tree to a pytree
    Lalr needs comments that aren't parsed along with newlines to be ignored
    We collect those with callbacks and then reintegrate them during the
    conversion to pytree
    """

    def __init__(self):
        self._comments = []
        self._all_newlines = []
        self._comment_mapping: CommentMapping = {}
        self._orphan_comment_mapping: StandAloneCommentMapping = defaultdict(
            list
        )
        self._header_comments: List[Token] = []
        self.indenter = PythonIndenter()
        self.lalr = self._create_lalr_parser()

    def _create_lalr_parser(self):
        return Lark.open_from_package(
            "mamushi",
            "grammar.lark",
            ["parsing"],
            parser="lalr",
            start="module",
            postlex=self.indenter,
            keep_all_tokens=True,
            propagate_positions=True,
            lexer_callbacks={
                "COMMENT": self._comments.append,
                "_NEWLINE": self._record_all_newlines,
            },
            maybe_placeholders=False,
        )

    def _record_all_newlines(self, token: Token):
        self._all_newlines.append(token)
        return token

    @staticmethod
    def _preprocess(code: str) -> str:
        return re.sub(r"[ \t]+\n", "\n", code, re.MULTILINE) + "\n"

    def _clear_comments(self):
        self._comments.clear()
        self._comment_mapping.clear()
        self._orphan_comment_mapping.clear()
        self._header_comments.clear()
        self._all_newlines.clear()

    def parse(self, code):
        self._clear_comments()
        lark_tree = self.lalr.parse(self._preprocess(code))
        self._generate_comment_associations(lark_tree)
        pytree = self._to_pytree(lark_tree)
        return pytree

    @staticmethod
    def _break_down_comments(t: Token) -> List[Token]:
        res = []
        nlines = 0
        newline = t.value.removeprefix("\n").rstrip(" \t").removesuffix("\n")
        for i, line in enumerate(re.split("\n", newline)):
            line = line.lstrip()
            if not line:
                nlines += 1
            if not line.startswith("#"):
                continue
            res.append(
                Token(
                    type=tokens.STANDALONE_COMMENT,
                    value=("\n" * nlines) + line,
                    line=t.line + i,  # type: ignore
                )
            )
            nlines = 0
        if res:
            res[-1].value += "\n" * nlines
        return res

    @staticmethod
    def _token_id(token: Token) -> Tuple[Any, ...]:
        return (
            token.value,
            token.type,
            token.column,
            token.end_pos,
            token.line,
        )

    def _generate_comment_associations(self, tree: Tree):
        """
        Run a BFS on the tree to find the final leaves of each lines
        where we can append the ignored comments in the final tree
        return a mapping of leaves to comment
        """

        # handle trailing comments first
        comments = self._comments
        comments.sort(key=lambda c: c.line)
        cmt_idx = {c.line: c for c in comments}

        # retrieve orphaned comments from ignored newlines
        # these are usually comments in between arguments to a call
        orphaned_comments = list(
            set(self._all_newlines) - set(self.indenter.processed_newlines)
        )
        orphaned_comments = [
            el
            for t in orphaned_comments
            for el in self._break_down_comments(t)
            if "#" in t
        ]
        orphaned_comments.sort(key=lambda c: c.line)
        o_cmt_idx = {c.line: c for c in orphaned_comments}

        queue = [tree]
        terminal_leaves: Dict[
            int, Token
        ] = {}  # parent node and index of child

        # we first traverse to find the last token on each potentially relevant line
        while queue:
            node = queue.pop()
            # if the node does not cover any lines with comments
            # or is a leaf, we can skip
            if isinstance(node, Token):
                continue
            for i, child in enumerate(node.children):
                if (
                    isinstance(child, Token)
                    and (child.line and child.end_pos)
                    and (
                        child.line not in terminal_leaves
                        or child.end_pos  # type: ignore
                        >= terminal_leaves[child.line].end_pos
                    )
                ):
                    # we handle the case where a comment is the first node later
                    if child.type == NEWLINE and child.line == 1:
                        continue
                    else:
                        terminal_leaves[child.line] = child
                else:
                    queue.append(child)

        # create a mapping for trailing comments
        self._comment_mapping = {
            self._token_id(t): cmt_idx[line]
            for line, t in terminal_leaves.items()
            if line in cmt_idx
        }

        # we need to handle the case where the first line is a comment
        if comments and comments[0].line == 1 and 1 not in terminal_leaves:
            self._header_comments = [cmt_idx[1]]

        # handle the orphaned comments last
        for (
            line,
            comment,
        ) in o_cmt_idx.items():  # o_cmt_idx is sorted (p3.6+)
            attach_line = line
            while attach_line not in terminal_leaves:
                attach_line -= 1
                if attach_line < 0:
                    self._header_comments.append(comment)
                    break
            if attach_line < 0:
                continue
            t = terminal_leaves[attach_line]
            key_token = (t.value, t.type, t.column, t.end_pos, t.line)
            self._orphan_comment_mapping[key_token].append(comment)

    def _to_pytree(self, lark_tree: Tree) -> Node:
        def _transform(tree: Tree):
            """
            Convert a Lark tree to Pytree
            """
            subnodes = []
            for i, child in enumerate(tree.children):
                if isinstance(child, Tree):
                    subnodes.append(_transform(child))

                else:
                    # we store the original cursor of the subnodes
                    # for when we need to insert comments beforehand (whitespace)
                    subnode_cursor = len(subnodes)

                    if child.type in tokens.WHITESPACE and "#" in child.value:
                        subnodes.append(
                            Leaf(
                                type=child.type,
                                value="",
                            )
                        )
                        for comment in self._break_down_comments(child):
                            subnodes.append(
                                Leaf(
                                    type=tokens.STANDALONE_COMMENT,
                                    value=comment.value,
                                )
                            )

                    else:
                        # append current child to list of subnodes
                        subnodes.append(
                            Leaf(
                                type=child.type,
                                value=child.value,
                            )
                        )

                    # process any potential trailing comments
                    child_id = (
                        self._token_id(child)
                        if child.type
                        not in {tokens.COMMENT, tokens.STANDALONE_COMMENT}
                        else ("", "", 0, 0)
                    )

                    if (
                        self._comment_mapping
                        and child_id in self._comment_mapping
                    ):
                        comment = self._comment_mapping[child_id]
                        # if the current node is a newline, we want the trailing comment BEFORE
                        if child.type == NEWLINE:
                            subnodes.insert(
                                subnode_cursor,
                                Leaf(type=comment.type, value=comment.value),
                            )
                            subnode_cursor += 1
                        else:
                            subnodes.append(
                                Leaf(type=comment.type, value=comment.value)
                            )

                    # handle the standalone comments last
                    if (
                        self._orphan_comment_mapping
                        and child_id in self._orphan_comment_mapping
                    ):
                        subnodes += [
                            Leaf(type=c.type, value=c.value)
                            for c in self._orphan_comment_mapping[child_id]
                        ]

            node = Node(type=tree.data, children=[])
            for leaf in subnodes:
                node.append_child(leaf)
            return node

        module = _transform(lark_tree)

        self._header_comments.sort(key=lambda x: x.line, reverse=True)  # type: ignore
        for c in self._header_comments:
            module.children.insert(
                0,
                Leaf(
                    type=c.type,
                    value=c.value,
                ),
            )

        return module
