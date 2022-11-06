# EXPERIMENTAL VYPER PARSER
# https://github.com/vyperlang/vyper/
from typing import Any, Dict, Optional, Tuple
import re
from lark import Lark, Tree, Token
from lark.indenter import Indenter
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


class Parser(object):
    """
    Parse a vyper file using lark, converts the lark tree to a pytree
    Lalr needs comments that aren't parsed along with newlines to be ignored
    We collect those with callbacks and then reintegrate them during the
    conversion to pytree
    """

    def __init__(self):
        self._comments = []
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
            lexer_callbacks={"COMMENT": self._comments.append},
            maybe_placeholders=False,
        )

    @staticmethod
    def _preprocess(code: str) -> str:
        return re.sub(r"[ |\t]+\n", "\n", code, re.MULTILINE) + "\n"

    def parse(self, code):
        self._comments.clear()
        lark_tree = self.lalr.parse(self._preprocess(code))
        comment_mappings = self._generate_comment_associations(lark_tree)
        pytree = self._to_pytree(lark_tree, comment_mappings)
        return pytree

    def _generate_comment_associations(self, tree):
        """
        Run a BFS on the tree to find the final leaves of each lines
        where we can append the ignored comments in the final tree
        return a mapping of leaves to comment
        """
        comments = list(self._comments)
        comments.sort(key=lambda c: c.line)
        latest_comment_line = comments[-1].line if comments else 0
        cmt_idx = {c.line: c for c in comments}
        comment_lines = [
            cmt_idx[i] if i in cmt_idx else None
            for i in range(latest_comment_line + 1)
        ]

        queue = [tree]
        terminal_leaves = {}  # parent node and index of child
        while queue:
            node = queue.pop()
            # if the node does not cover any lines with comments
            # or is a leaf, we can skip
            if isinstance(node, Token):
                continue
            elif not any(
                comment_lines[
                    node.meta.line : min(
                        latest_comment_line, node.meta.end_line
                    )
                    + 1
                ]
            ):
                continue
            for i, child in enumerate(node.children):
                if isinstance(child, Token) and child.line in cmt_idx:
                    if (
                        child.line not in terminal_leaves
                        or child.end_column
                        >= terminal_leaves[child.line].end_column
                    ):
                        # we handle the case where a comment is the first node later
                        if child.type == NEWLINE and i == 0:
                            continue
                        else:
                            terminal_leaves[child.line] = child
                else:
                    queue.append(child)

        comment_mapping = {
            (t.value, t.type, t.column, t.end_column, t.line): cmt_idx[line]
            for line, t in terminal_leaves.items()
        }
        # we need to handle the case where the first line is a standalone comment
        if comments and comments[0].line == 1 and 1 not in terminal_leaves:
            comment_mapping[(-1,)] = cmt_idx[1]
        return comment_mapping

    def _to_pytree(
        self, lark_tree: Tree, comment_mapping: Optional[Dict[Tuple, Token]]
    ) -> Node:
        def _transform(tree: Tree):
            """
            Convert a Lark tree to Pytree
            """
            subnodes = []
            for i, child in enumerate(tree.children):

                if isinstance(child, Tree):
                    subnodes.append(_transform(child))

                else:
                    child_id = (
                        child.value,
                        child.type,
                        child.column,
                        child.end_column,
                        child.line,
                    )
                    if (
                        comment_mapping
                        and child_id in comment_mapping
                        and child.type == NEWLINE
                    ):
                        comment = comment_mapping[child_id]
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
                        if comment_mapping and child_id in comment_mapping:
                            comment = comment_mapping[child_id]
                            subnodes.append(
                                Leaf(type=comment.type, value=comment.value)
                            )
            node = Node(type=tree.data, children=[])
            for leaf in subnodes:
                node.append_child(leaf)
            return node

        module = _transform(lark_tree)
        if comment_mapping and (-1,) in comment_mapping:
            module.children.insert(
                0,
                Leaf(
                    type=comment_mapping[(-1,)].type,
                    value=comment_mapping[(-1,)].value,
                ),
            )

        return module
