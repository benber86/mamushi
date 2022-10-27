from lark import Token
from lark.visitors import Transformer_InPlaceRecursive

from parsing import tokens
from parsing.parser import parse_string_to_tokenless_ast


class NullifyDocstrings(Transformer_InPlaceRecursive):
    def DOCSTRING(self, args):
        return Token(type_=tokens.DOCSTRING, value="")


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
