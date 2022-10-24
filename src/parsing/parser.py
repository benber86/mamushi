# EXPERIMENTAL VYPER PARSER
# https://github.com/vyperlang/vyper/

from lark import Lark, Tree
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
    OPEN_PAREN_types = OPENING_BRACKETS
    CLOSE_PAREN_types = CLOSING_BRACKETS
    INDENT_type = INDENT
    DEDENT_type = DEDENT
    tab_len = 4


_lark_grammar = None


def vyper_grammar():
    global _lark_grammar
    if _lark_grammar is None:
        _lark_grammar = Lark.open_from_package(
            "parsing",
            "grammar.lark",
            ("/",),
            parser="lalr",
            start="module",
            postlex=PythonIndenter(),
            keep_all_tokens=True,
            maybe_placeholders=False
        )
    return _lark_grammar


def _to_pytree(lark_tree: Tree) -> Node:

    module = Node(type="module", children=[])

    def _transform(tree: Tree, prev_type=None):
        """
        Convert a Lark tree to Pytree
        """
        subnodes = []
        for i, child in enumerate(tree.children):

            if isinstance(child, Tree):
                subnodes.append(_transform(child, prev_type))

            else:
                subnodes.append(
                    Leaf(
                        type=child.type,
                        value=child.value,
                    )
                )
                prev_type = child.type
        node = Node(type=tree.data, children=[])
        for leaf in subnodes:
            node.append_child(leaf)
        module.append_child(node)
        return node

    return _transform(lark_tree)


def parse_string(code: str) -> Node:
    return _to_pytree(vyper_grammar().parse(code + "\n"))
