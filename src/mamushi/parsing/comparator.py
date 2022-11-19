from lark import Token
from lark.visitors import Transformer_InPlaceRecursive

from mamushi.parsing import tokens
from lark import Lark, Tree
from mamushi.parsing.parser import PythonIndenter

_plain_lark_grammar = None


class NullifyStringsAndNewLines(Transformer_InPlaceRecursive):
    def DOCSTRING(self, args):
        return Token(type_=tokens.DOCSTRING, value="")

    def _NEWLINE(self, args):
        return Token(type_=tokens.NEWLINE, value="")

    def STRING(self, args):
        return Token(type_=tokens.STRING, value="")


def plain_grammar():
    global _plain_lark_grammar
    if _plain_lark_grammar is None:
        return Lark.open_from_package(
            "mamushi",
            "grammar.lark",
            ["parsing"],
            parser="lalr",
            start="module",
            postlex=PythonIndenter(),
            keep_all_tokens=False,
            maybe_placeholders=False,
        )


def parse_string_to_tokenless_ast(code: str) -> Tree:
    return plain_grammar().parse(code + "\n\n")


def compare_ast(src: str, dest: str) -> bool:
    """
    Generates two ASTs with no punctuation tokens  and uses a transformer to
    remove docstrings (since these are reformatted and not ignored)
    and newlines (since we might reformat comments) then compares
    the two trees to ensure no syntactic changes were introduced
    """
    src_tree = parse_string_to_tokenless_ast(src)
    dest_tree = parse_string_to_tokenless_ast(dest)
    NullifyStringsAndNewLines().transform(src_tree)
    NullifyStringsAndNewLines().transform(dest_tree)
    return src_tree == dest_tree
