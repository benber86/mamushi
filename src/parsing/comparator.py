from lark import Token
from lark.visitors import Transformer_InPlaceRecursive

from parsing import tokens
from lark import Lark, Tree
from parsing.parser import PythonIndenter

_plain_lark_grammar = None


class NullifyDocstrings(Transformer_InPlaceRecursive):
    def DOCSTRING(self, args):
        return Token(type_=tokens.DOCSTRING, value="")


def plain_grammar():
    global _plain_lark_grammar
    if _plain_lark_grammar is None:
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


def parse_string_to_tokenless_ast(code: str) -> Tree:
    return plain_grammar().parse(code + "\n\n")


def compare_ast(src: str, dest: str) -> bool:
    """
    Generates two ASTs with no punctuation tokens  and uses a transformer to
    remove docstrings (since these are reformatted and not ignored) then compares
    hashes of the two trees to ensure no syntactic changes were introduced
    """
    src_tree = parse_string_to_tokenless_ast(src)
    dest_tree = parse_string_to_tokenless_ast(dest)
    NullifyDocstrings().transform(src_tree)
    NullifyDocstrings().transform(dest_tree)
    return src_tree == dest_tree
