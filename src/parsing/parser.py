# EXPERIMENTAL VYPER PARSER
# https://github.com/vyperlang/vyper/
from collections import defaultdict
from typing import Any, Dict, Optional, Tuple, Union, List, Set
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
        self._stand_alone_comments = []
        self._comment_mapping: CommentMapping = {}
        self._sa_comment_mapping: StandAloneCommentMapping = defaultdict(list)
        self._header_comments: List[Token] = []
        self.lalr = self._create_lalr_parser()
        self._dedent_counts: DedentCount = defaultdict(int)

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
            comment_type = tokens.STANDALONE_COMMENT
            self._stand_alone_comments.append(
                Token(
                    type=comment_type,
                    value=("\n" * nlines) + line,
                    line=token.line + i,  # type: ignore
                )
            )
            nlines = 0
        # we clear the newline if we've extracted any comment
        if has_comments:
            token.value = "\n" * nlines
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
        self._dedent_counts.clear()

    def parse(self, code):
        self._clear_comments()
        lark_tree = self.lalr.parse(self._preprocess(code))
        self._generate_comment_associations(lark_tree)
        pytree = self._to_pytree(lark_tree)
        return pytree

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
        comments = list(self._comments)
        comments.sort(key=lambda c: c.line)
        cmt_idx = {c.line: c for c in comments}

        # stand alone comments
        standalone_comments = list(self._stand_alone_comments)
        standalone_comments.sort(key=lambda c: c.line)
        sa_cmt_idx = {c.line: c for c in standalone_comments}

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
                    # because lark will parse different dedent tokens with similar
                    # coordinates, we need to keep track of where we stand
                    if child.type == tokens.DEDENT:
                        self._dedent_counts[self._token_id(child)] += 1
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
            key_token = (t.value, t.type, t.column, t.end_pos, t.line)
            self._sa_comment_mapping[key_token].append(comment)

    def _to_pytree(self, lark_tree: Tree) -> Node:

        local_dedent_counter: DedentCount = defaultdict(int)

        def _get_leading_lines(string: str) -> int:
            """Get number of leading line returns"""
            return len(string) - len(string.lstrip("\n"))

        def _get_trailing_lines(string: str) -> int:
            """Get number of trailin line returns"""
            return len(string) - len(string.rstrip("\n"))

        def _remove_leading_line(comments: List[Leaf]) -> List[Leaf]:
            if comments:
                leading_comment = comments[0].value
                if len(leading_comment) > 0 and leading_comment[0] == "\n":
                    leading_comment = leading_comment[1:]
                comments[0].value = leading_comment
            return comments

        def _split_comment_queue(
            queue: List[Leaf],
        ) -> Tuple[List[Leaf], List[Leaf]]:
            """
            if a queue of standalone comments has a newline (2 new lines)
            we want to keep all comments before that before the dedent
            and all comments after, after the dedent
            """
            before = []
            while queue:
                if _get_leading_lines(queue[0].value) > 1:
                    break
                before.append(queue.pop(0))
            return before, queue

        def _transform(tree: Tree):
            """
            Convert a Lark tree to Pytree
            """
            subnodes = []
            sa_comment_queue: List[Leaf] = []
            for i, child in enumerate(tree.children):

                if isinstance(child, Tree):
                    subnodes.append(_transform(child))

                else:
                    # we store the original cursor of the subnodes
                    # for when we need to insert comments beforehand (whitespace)
                    subnode_cursor = len(subnodes)

                    # append current child to list of subnodes
                    subnodes.append(
                        Leaf(
                            type=child.type,
                            value=child.value,
                        )
                    )

                    """ process any potential trailing comments """
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
                        # if it's an indent/dedent, we want the trailing comment
                        # inserted back before the preceding newline
                        elif child.type in {tokens.INDENT, tokens.DEDENT}:
                            subnodes.insert(
                                subnode_cursor - 1,
                                Leaf(type=comment.type, value=comment.value),
                            )
                            subnode_cursor += 1
                        # otherwise append any trailing comments
                        else:
                            subnodes.append(
                                Leaf(type=comment.type, value=comment.value)
                            )

                    """ handle the standalone comments last """
                    if (
                        self._sa_comment_mapping
                        and child_id in self._sa_comment_mapping
                    ):

                        sa_comment_queue = [
                            Leaf(type=c.type, value=c.value)
                            for c in self._sa_comment_mapping[child_id]
                        ]

                        # we use the counter for repeat visit, we will always associate
                        # with final dedent (for instance after multiple nested ifs)
                        local_dedent_counter[child_id] += 1
                        if (
                            local_dedent_counter[child_id]
                            < self._dedent_counts[child_id]
                        ):
                            continue

                        if child.type not in tokens.WHITESPACE:
                            subnodes += sa_comment_queue
                        # if there's an indentation, we consider all standalone comments
                        # to be part of the body
                        elif child.type == tokens.INDENT:
                            subnodes += _remove_leading_line(sa_comment_queue)
                        # for newlines with no indentation
                        # we just want to move the sa comments before
                        elif child.type == tokens.NEWLINE:
                            # move trailing line return to the comment
                            sa_comment_queue[-1].value += "\n" * (
                                _get_trailing_lines(child.value) - 1
                            )
                            child.value = ""
                            subnodes = (
                                subnodes[:subnode_cursor]
                                + _remove_leading_line(sa_comment_queue)
                                + subnodes[subnode_cursor + 1 :]
                            )
                        else:
                            before_dedent, after_dedent = _split_comment_queue(
                                sa_comment_queue.copy()
                            )
                            before_dedent = _remove_leading_line(before_dedent)
                            if (
                                subnodes[subnode_cursor - 1].type
                                == tokens.NEWLINE
                            ):
                                # we need to move any trailing lines from the newline over to the comment
                                if after_dedent:
                                    after_dedent[0].value += subnodes[
                                        subnode_cursor - 1
                                    ].value
                                    subnodes[subnode_cursor - 1].value = ""

                            subnodes = (
                                subnodes[:subnode_cursor]
                                + before_dedent
                                + subnodes[subnode_cursor:]
                                + after_dedent
                            )
                        sa_comment_queue.clear()

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
