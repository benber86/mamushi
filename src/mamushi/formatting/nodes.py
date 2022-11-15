from typing import Union, List, Tuple

from mamushi.parsing import tokens
from mamushi.parsing.pytree import Leaf, Node

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


def ensure_visible(leaf: Leaf) -> None:
    """Make sure parentheses are visible.

    They could be invisible as part of some statements (see
    :func:`normalize_invisible_parens` and :func:`visit_import_from`).
    """
    if leaf.type == tokens.LPAR:
        leaf.value = "("
    elif leaf.type == tokens.RPAR:
        leaf.value = ")"


def is_one_sequence_between(
    opening: Leaf,
    closing: Leaf,
    leaves: List[Leaf],
    brackets: Tuple[str, str] = (tokens.LPAR, tokens.RPAR),
) -> bool:
    """Return True if content between `opening` and `closing` is a one-sequence."""
    if (opening.type, closing.type) != brackets:
        return False

    depth = closing.bracket_depth + 1
    for _opening_index, leaf in enumerate(leaves):
        if leaf is opening:
            break

    else:
        raise LookupError("Opening paren not found in `leaves`")

    commas = 0
    _opening_index += 1
    for leaf in leaves[_opening_index:]:
        if leaf is closing:
            break

        bracket_depth = leaf.bracket_depth
        if bracket_depth == depth and leaf.type == tokens.COMMA:
            commas += 1
            if leaf.parent and leaf.parent.type in {
                tokens.ARGUMENTS,
                tokens.PARAMETERS,
            }:
                commas += 1
                break

    return commas < 2


def replace_child(old_child: LN, new_child: LN) -> None:
    """
    Side Effects:
        * If @old_child.parent is set, replace @old_child with @new_child in
        @old_child's underlying Node structure.
            OR
        * Otherwise, this function does nothing.
    """
    parent = old_child.parent
    if not parent:
        return

    child_idx = old_child.remove()
    if child_idx is not None:
        parent.insert_child(child_idx, new_child)
