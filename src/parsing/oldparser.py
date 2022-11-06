# EXPERIMENTAL VYPER PARSER
# https://github.com/vyperlang/vyper/
from typing import Any, Dict

from lark import Lark, Tree
from lark.indenter import Indenter
import re
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


_grammars: Dict[str, Any] = {}


def _get_grammar(tokens=True):
    return Lark.open_from_package(
        "parsing",
        "grammar.lark",
        ("/",),
        parser="lalr",
        start="module",
        postlex=PythonIndenter(),
        keep_all_tokens=tokens,
        maybe_placeholders=False,
    )


def vyper_grammar(tokens=True):
    global _grammars
    if tokens:
        if not _grammars.get("tokens", None):
            _grammars["tokens"] = _get_grammar(True)
        return _grammars["tokens"]
    else:
        if not _grammars.get("tokenless", None):
            _grammars["tokenless"] = _get_grammar(False)
        return _grammars["tokenless"]


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
    # remove whitespace on empty lines
    code = re.sub(r"[ |\t]+\n", "\n", code, re.MULTILINE)
    return _to_pytree(vyper_grammar().parse(code + "\n"))


def parse_string_to_tokenless_ast(code: str) -> Tree:
    return vyper_grammar(False).parse(code + "\n")
