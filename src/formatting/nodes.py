from typing import Union

from parsing import tokens
from parsing.pytree import Leaf, Node

LN = Union[Leaf, Node]


def wrap_in_parentheses(
    parent: Node, child: LN, *, visible: bool = True
) -> None:
    """Wrap `child` in parentheses.

    This replaces `child` with an atom holding the parentheses and the old
    child.  That requires moving the prefix.

    If `visible` is False, the leaves will be valueless (and thus invisible).
    """
    lpar = Leaf(tokens.LPAR, "(" if visible else "")
    rpar = Leaf(tokens.RPAR, ")" if visible else "")
    prefix = child.prefix
    child.prefix = ""
    index = child.remove() or 0
    new_child = Node(child.type, [lpar, child, rpar])
    new_child.prefix = prefix
    parent.insert_child(index, new_child)


def is_atom_with_invisible_parens(node: LN) -> bool:
    """Given a `LN`, determines whether it's an atom `node` with invisible
    parens. Useful in dedupe-ing and normalizing parens.
    """
    if isinstance(node, Leaf) or node.type != tokens.ATOM:
        return False

    first, last = node.children[0], node.children[-1]
    return (
        isinstance(first, Leaf)
        and first.type == tokens.LPAR
        and first.value == ""
        and isinstance(last, Leaf)
        and last.type == tokens.RPAR
        and last.value == ""
    )


def is_empty_lpar(leaf: Leaf) -> bool:
    return leaf.type == tokens.LPAR and leaf.value == ""


def is_empty_rpar(leaf: Leaf) -> bool:
    return leaf.type == tokens.RPAR and leaf.value == ""
