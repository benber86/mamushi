# EXPERIMENTAL VYPER PARSER
# https://github.com/vyperlang/vyper/
from collections import defaultdict
from typing import Any, Dict, Optional, Tuple, Union, List
import re
from lark import Lark, Tree, Token
from lark.indenter import Indenter
from parsing import tokens
from parsing.pytree import Leaf, Node
from parsing.tokens import (
    OPENING_BRACKETS,
    CLOSING_BRACKETS,
    NEWLINE,
    INDENT,
    DEDENT,
)


class PythonIndenter(Indenter):
    NL_type = NEWLINE
    OPEN_PAREN_types = list(OPENING_BRACKETS)
    CLOSE_PAREN_types = list(CLOSING_BRACKETS)
    INDENT_type = INDENT
    DEDENT_type = DEDENT
    tab_len = 4


CommentMapping = Dict[Tuple[Any, ...], Token]
StandAloneCommentMapping = Dict[Tuple[Any, ...], List[Token]]


class Parser(object):
    """
    Parse a vyper file using lark, converts the lark tree to a pytree
    Lalr needs comments that aren't parsed along with newlines to be ignored
    We collect those with callbacks and then reintegrate them during the
    conversion to pytree
    """

    def __init__(self):
        self._comments = []
        self._stand_alone_comments = []
        self._comment_mapping: CommentMapping = {}
        self._sa_comment_mapping: StandAloneCommentMapping = defaultdict(list)
        self._header_comments: List[Token] = []
        self.lalr = self._create_lalr_parser()

    def _create_lalr_parser(self):
        return Lark.open_from_package(
            "parsing",
            "grammar.lark",
            ("/",),
            parser="lalr",
            start="module",
            postlex=PythonIndenter(),
            keep_all_tokens=True,
            propagate_positions=True,
            lexer_callbacks={
                "COMMENT": self._comments.append,
                "_NEWLINE": self._process_ignored_newlines,
            },
            maybe_placeholders=False,
        )

    def _process_ignored_newlines(self, token: Token):
        consumed = 0
        nlines = 0
        ignored_lines = 0
        has_comments = False
        lines = re.split("\r?\n", token.value)
        for i, line in enumerate(lines):
            consumed += len(line) + 1
            line = line.lstrip()
            if not line:
                nlines += 1
            if not line.startswith("#"):
                continue
            has_comments = True
            if i == ignored_lines:
                comment_type = tokens.COMMENT
            else:
                comment_type = tokens.STANDALONE_COMMENT
            self._stand_alone_comments.append(
                Token(
                    type=comment_type,
                    value=("\n" * max(0, nlines - 1)) + line,
                    line=token.line + i,
                )
            )
        # we clear the newline if we've extracted any comment
        if has_comments:
            token.value = ""
        return token

    @staticmethod
    def _preprocess(code: str) -> str:
        return re.sub(r"[ |\t]+\n", "\n", code, re.MULTILINE) + "\n"

    def _clear_comments(self):
        self._comments.clear()
        self._stand_alone_comments.clear()
        self._comment_mapping.clear()
        self._sa_comment_mapping.clear()
        self._header_comments.clear()

    def parse(self, code):
        self._clear_comments()
        lark_tree = self.lalr.parse(self._preprocess(code))
        self._generate_comment_associations(lark_tree)
        pytree = self._to_pytree(lark_tree)
        return pytree

    def _generate_comment_associations(self, tree: Tree):
        """
        Run a BFS on the tree to find the final leaves of each lines
        where we can append the ignored comments in the final tree
        return a mapping of leaves to comment
        """
        # handle trailing comments first
        comments = list(self._comments)
        comments.sort(key=lambda c: c.line)
        latest_comment_line = comments[-1].line if comments else 0
        cmt_idx = {c.line: c for c in comments}
        comment_lines = [
            cmt_idx[i] if i in cmt_idx else None
            for i in range(latest_comment_line + 1)
        ]

        # stand alone comments
        standalone_comments = list(self._stand_alone_comments)
        standalone_comments.sort(key=lambda c: c.line)
        latest_sa_comment_line = (
            standalone_comments[-1].line if standalone_comments else 0
        )
        sa_cmt_idx = {c.line: c for c in standalone_comments}
        standalone_comment_lines = [
            sa_cmt_idx[i] if i in sa_cmt_idx else None
            for i in range(latest_sa_comment_line + 1)
        ]

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
            # fmt: off
            elif (not any(comment_lines[node.meta.line:min(latest_comment_line, node.meta.end_line) + 1]) and not
                    any(standalone_comment_lines[node.meta.line - 1:min(latest_sa_comment_line, node.meta.end_line) + 1])):
                continue
            # fmt: on
            for i, child in enumerate(node.children):
                if (
                    isinstance(child, Token)
                    and (child.line and child.end_column)
                    and (
                        child.line not in terminal_leaves
                        or child.end_column  # type: ignore
                        >= terminal_leaves[child.line].end_column
                    )
                ):
                    # we handle the case where a comment is the first node later
                    if (child.type == NEWLINE and i == 0) or (
                        child.type == tokens.DEDENT
                    ):
                        continue
                    else:
                        terminal_leaves[child.line] = child
                else:
                    queue.append(child)

        # create a mapping for trailing comments
        self._comment_mapping = {
            (t.value, t.type, t.column, t.end_column, t.line): cmt_idx[line]
            for line, t in terminal_leaves.items()
            if line in cmt_idx
        }

        # we need to handle the case where the first line is a comment
        if comments and comments[0].line == 1 and 1 not in terminal_leaves:
            self._header_comments = [cmt_idx[1]]

        # and one for standalone comments
        for (
            line,
            comment,
        ) in sa_cmt_idx.items():  # sa_cmt_idx is sorted (p3.6+)
            attach_line = line
            while attach_line not in terminal_leaves:
                attach_line -= 1
                if attach_line < 0:
                    self._header_comments.append(comment)
                    break
            if attach_line < 0:
                continue
            t = terminal_leaves[attach_line]
            self._sa_comment_mapping[
                (t.value, t.type, t.column, t.end_column, t.line)
            ].append(comment)

    def _to_pytree(self, lark_tree: Tree) -> Node:
        def _is_before_indent(tree: Tree, index: int) -> bool:
            if index + 2 >= len(tree.children):
                return False
            if not (
                isinstance(tree.children[index + 1], Tree)
                and len(tree.children[index + 1].children) > 1
            ):
                return False
            if (
                isinstance(tree.children[index + 1].children[0], Leaf)
                and tree.children[index + 1].children[0].type
                == tokens.WHITESPACE
                and isinstance(tree.children[index + 1].children[1], Leaf)
                and tree.children[index + 1].children[1].type == tokens.INDENT
            ):
                return True
            return False

        def _transform(tree: Tree):
            """
            Convert a Lark tree to Pytree
            """
            subnodes = []
            sa_comment_queue: List[Leaf] = []
            for i, child in enumerate(tree.children):

                if isinstance(child, Tree):
                    if sa_comment_queue:
                        for j, subchild in enumerate(child.children):
                            # process the potential standalone queue, appending htem after all whitespace
                            if isinstance(
                                subchild, Tree
                            ) or subchild.type not in {
                                tokens.NEWLINE,
                                tokens.INDENT,
                            }:
                                child.children = (
                                    child.children[:j]
                                    + sa_comment_queue
                                    + child.children[j:]
                                )
                                sa_comment_queue.clear()
                                break
                    subnodes.append(_transform(child))

                else:
                    child_id = (
                        (
                            child.value,
                            child.type,
                            child.column,
                            child.end_column,
                            child.line,
                        )
                        if child.type
                        not in {tokens.COMMENT, tokens.STANDALONE_COMMENT}
                        else ("", "", 0, 0)
                    )
                    if (
                        self._comment_mapping
                        and child_id in self._comment_mapping
                        and child.type == NEWLINE
                    ):
                        comment = self._comment_mapping[child_id]
                        # if the comment is associated to a newline we want to insert it BEFORE
                        subnodes.append(
                            Leaf(type=comment.type, value=comment.value)
                        )
                        subnodes.append(
                            Leaf(
                                type=child.type,
                                value=child.value,
                            )
                        )
                    else:
                        subnodes.append(
                            Leaf(
                                type=child.type,
                                value=child.value,
                            )
                        )
                        if (
                            self._comment_mapping
                            and child_id in self._comment_mapping
                        ):
                            comment = self._comment_mapping[child_id]
                            subnodes.append(
                                Leaf(type=comment.type, value=comment.value)
                            )
                    # append the standalone comments last
                    if (
                        self._sa_comment_mapping
                        and child_id in self._sa_comment_mapping
                    ):
                        sa_comment_queue = [
                            Leaf(type=c.type, value=c.value)
                            for c in self._sa_comment_mapping[child_id]
                        ]
                    # if there's whitespace / indentation coming up
                    # hold on processing the queue
                    if _is_before_indent(tree, i):
                        continue
                    else:
                        subnodes += sa_comment_queue
                        sa_comment_queue.clear()

            node = Node(type=tree.data, children=[])
            for leaf in subnodes:
                node.append_child(leaf)
            return node

        module = _transform(lark_tree)

        self._header_comments.sort(key=lambda x: x.line, reverse=True)
        for c in self._header_comments:
            module.children.insert(
                0,
                Leaf(
                    type=c.type,
                    value=c.value,
                ),
            )

        return module
