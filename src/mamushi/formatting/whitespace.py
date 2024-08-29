from typing import Final
from typing import Optional, TypeVar, Union
from mamushi.parsing import tokens
from mamushi.parsing.pytree import Node, Leaf

T = TypeVar("T")
LN = Union[Leaf, Node]
ALWAYS_NO_SPACE: Final = tokens.CLOSING_BRACKETS | {
    tokens.COMMA,
    tokens.COLON,
    tokens.STANDALONE_COMMENT,
    tokens.DOCSTRING,
}


def whitespace(leaf: Leaf) -> str:
    """
    Handle adding whitespace or not before tokens
    Adapted from black
    TODO: complexity too high, needs to be refactored
    """
    NO: Final = ""
    SPACE: Final = " "
    DOUBLESPACE: Final = "  "
    t = leaf.type
    p = leaf.parent
    v = leaf.value

    if t in ALWAYS_NO_SPACE:
        return NO

    if t == tokens.COMMENT:
        return DOUBLESPACE

    if not p:
        return SPACE

    if p.type == tokens.DECORATOR:
        return NO

    prev = leaf.prev_sibling

    if not prev:
        prevp = preceding_leaf(p)
        if not prevp or prevp.type in tokens.OPENING_BRACKETS:
            return NO
        if prevp.type == tokens.TILDE:
            return NO
        # kwargs with expr assignment
        if (
            prevp.type == tokens.EQUAL
            and prevp.parent
            and prevp.parent.type == tokens.KWARG
        ):
            return NO

        elif (
            prevp.parent
            and prevp.parent.type in tokens.UNARY
            and prevp.type in tokens.MATH_OPERATORS
        ):
            return NO

        elif (
            prevp.parent
            and prevp.parent.parent
            and prevp.parent.parent.type == tokens.INITIALIZES_STMT
        ):
            return NO

    elif p.type == tokens.KWARG:
        if prev.type != tokens.COMMA:
            return NO

    elif prev.type in tokens.OPENING_BRACKETS:
        return NO

    elif t == tokens.EQUAL and prev.type in tokens.ASSIGN_OPERATORS:
        return NO

    elif p.type == tokens.IMPORT:
        # handle imports
        if (
            (prev.type != tokens.IMPORT_FROM and t == tokens.DOT)
            or prev.type == tokens.DOT
            and t != tokens.IMPORT_NAME
        ):
            return NO

    elif p.type in {tokens.ATTRIBUTE, tokens.IMPORTED_TYPE}:
        # variable access
        if t == tokens.DOT or prev.type == tokens.DOT:
            return NO

    elif (
        p.type.endswith(tokens.DEF_SUFFIX)
        or p.type.endswith(tokens.GETTER_SUFIX)
        or p.type
        in {
            tokens.FUNCTION_SIG,
            tokens.CALL,
            tokens.EXTERNAL_CALL,
            tokens.EMPTY,
            tokens.ABI_DECODE,
            tokens.SUBSCRIPT,
            tokens.INDEXED_ARGS,
            tokens.LOG_STMT,
            tokens.CONSTANT,
            tokens.IMPLEMENTS,
            tokens.USES,
            tokens.IMMUTABLE,
        }
    ):
        # no parentheses on calls, function sigs, logs and defs
        # except for returns
        if t == tokens.LPAR and prev.type not in {tokens.RETURN_TYPE}:
            return NO

        if t == tokens.LSQB:
            return NO

    if p.type == tokens.DECORATOR:
        # decorators
        return NO

    elif v.isnumeric() and p.type in tokens.UNARY:
        # no space for signed numbers
        return NO

    return SPACE


def preceding_leaf(node: Optional[LN]) -> Optional[Leaf]:
    """Return the first leaf that precedes `node`, if any."""
    while node:
        res = node.prev_sibling
        if res:
            if isinstance(res, Leaf):
                return res

            try:
                return list(res.leaves())[-1]

            except IndexError:
                return None

        node = node.parent
    return None
