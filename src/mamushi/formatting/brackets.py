"""Builds on top of nodes.py to track brackets."""

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple, Union
from mamushi.parsing import tokens
from typing import Final
from mamushi.parsing.pytree import Leaf, Node


# types

LN = Union[Leaf, Node]
Depth = int
LeafID = int
NodeType = str
Priority = int


COMPREHENSION_PRIORITY: Final = 20
COMMA_PRIORITY: Final = 18
TERNARY_PRIORITY: Final = 16
LOGIC_PRIORITY: Final = 14
STRING_PRIORITY: Final = 12
COMPARATOR_PRIORITY: Final = 10
MATH_PRIORITIES: Final = {
    tokens.VBAR: 9,
    tokens.CARET: 8,
    tokens.AMPERSAND: 7,
    tokens.LEFTSHIFT: 6,
    tokens.RIGHTSHIFT: 6,
    tokens.PLUS: 5,
    tokens.MINUS: 5,
    tokens.STAR: 4,
    tokens.SLASH: 4,
    tokens.PERCENT: 4,
    tokens.AT: 4,
    tokens.TILDE: 3,
    tokens.DOUBLESTAR: 2,
}
DOT_PRIORITY: Final = 1


class BracketMatchError(Exception):
    """Raised when an opening bracket is unable to be matched to a closing bracket."""


@dataclass
class BracketTracker:
    """Keeps track of brackets on a line."""

    depth: int = 0
    bracket_match: Dict[Tuple[Depth, NodeType], Leaf] = field(
        default_factory=dict
    )
    delimiters: Dict[LeafID, Priority] = field(default_factory=dict)
    previous: Optional[Leaf] = None
    _for_loop_depths: List[int] = field(default_factory=list)
    _lambda_argument_depths: List[int] = field(default_factory=list)
    invisible: List[Leaf] = field(default_factory=list)

    def mark(self, leaf: Leaf) -> None:
        """Mark `leaf` with bracket-related metadata. Keep track of delimiters.

        All leaves receive an int `bracket_depth` field that stores how deep
        within brackets a given leaf is. 0 means there are no enclosing brackets
        that started on this line.

        If a leaf is itself a closing bracket, it receives an `opening_bracket`
        field that it forms a pair with. This is a one-directional link to
        avoid reference cycles.

        If a leaf is a delimiter (a token on which Black can split the line if
        needed) and it's on depth 0, its `id()` is stored in the tracker's
        `delimiters` field.
        """
        if leaf.type == tokens.COMMENT:
            return

        self.maybe_decrement_after_for_loop_variable(leaf)
        if leaf.type in tokens.CLOSING_BRACKETS:
            self.depth -= 1
            try:
                opening_bracket = self.bracket_match.pop(
                    (self.depth, leaf.type)
                )
            except KeyError as e:
                raise BracketMatchError(
                    "Unable to match a closing bracket to the following opening"
                    f" bracket: {leaf}"
                ) from e
            leaf.opening_bracket = opening_bracket
            if not leaf.value:
                self.invisible.append(leaf)
        leaf.bracket_depth = self.depth
        if self.depth == 0:
            delim = is_split_before_delimiter(leaf, self.previous)
            if delim and self.previous is not None:
                self.delimiters[id(self.previous)] = delim
            else:
                delim = is_split_after_delimiter(leaf, self.previous)
                if delim:
                    self.delimiters[id(leaf)] = delim
        if leaf.type in tokens.OPENING_BRACKETS:
            self.bracket_match[
                self.depth, tokens.BRACKET_MAP[leaf.type]
            ] = leaf
            self.depth += 1
            if not leaf.value:
                self.invisible.append(leaf)
        self.previous = leaf
        self.maybe_increment_for_loop_variable(leaf)

    def any_open_brackets(self) -> bool:
        """Return True if there is an yet unmatched open bracket on the line."""
        return bool(self.bracket_match)

    def max_delimiter_priority(
        self, exclude: Iterable[LeafID] = ()
    ) -> Priority:
        """Return the highest priority of a delimiter found on the line.

        Values are consistent with what `is_split_*_delimiter()` return.
        Raises ValueError on no delimiters.
        """
        return max(v for k, v in self.delimiters.items() if k not in exclude)

    def delimiter_count_with_priority(self, priority: Priority = 0) -> int:
        """Return the number of delimiters with the given `priority`.

        If no `priority` is passed, defaults to max priority on the line.
        """
        if not self.delimiters:
            return 0

        priority = priority or self.max_delimiter_priority()
        return sum(1 for p in self.delimiters.values() if p == priority)

    def maybe_increment_for_loop_variable(self, leaf: Leaf) -> bool:
        """In a for loop, or comprehension, the variables are often unpacks.

        To avoid splitting on the comma in this situation, increase the depth of
        tokens between `for` and `in`.
        """
        if leaf.type == tokens.FOR and leaf.value == "for":
            self.depth += 1
            self._for_loop_depths.append(self.depth)
            return True

        return False

    def maybe_decrement_after_for_loop_variable(self, leaf: Leaf) -> bool:
        """See `maybe_increment_for_loop_variable` above for explanation."""
        if (
            self._for_loop_depths
            and self._for_loop_depths[-1] == self.depth
            and leaf.type == tokens.IN
            and leaf.value == "in"
        ):
            self.depth -= 1
            self._for_loop_depths.pop()
            return True

        return False


def is_split_after_delimiter(
    leaf: Leaf, previous: Optional[Leaf] = None
) -> Priority:
    """Return the priority of the `leaf` delimiter, given a line break after it.

    The delimiter priorities returned here are from those delimiters that would
    cause a line break after themselves.

    Higher numbers are higher priority.
    """
    if leaf.type == tokens.COMMA:
        return COMMA_PRIORITY

    return 0


def is_split_before_delimiter(
    leaf: Leaf, previous: Optional[Leaf] = None
) -> Priority:
    """Return the priority of the `leaf` delimiter, given a line break before it.

    The delimiter priorities returned here are from those delimiters that would
    cause a line break before themselves.

    Higher numbers are higher priority.
    """

    if (
        leaf.type == tokens.DOT
        and leaf.parent
        and leaf.parent.type != tokens.IMPORT
        and (previous is None or previous.type in tokens.CLOSING_BRACKETS)
    ):
        return DOT_PRIORITY

    if leaf.type in tokens.MATH_OPERATORS and leaf.parent:
        return MATH_PRIORITIES[leaf.type]

    if leaf.type in tokens.COMPARATORS:
        return COMPARATOR_PRIORITY

    if (
        leaf.type == tokens.STRING
        and previous is not None
        and previous.type == tokens.STRING
    ):
        return STRING_PRIORITY

    if (
        leaf.value == "for"
        and leaf.parent
        and leaf.parent.type == tokens.FOR_STMT
    ):
        if not isinstance(leaf.prev_sibling, Leaf):
            return COMPREHENSION_PRIORITY

    if (
        leaf.value == "if"
        and leaf.parent
        and leaf.parent.type in {tokens.IF_STMT, tokens.COND_EXEC}
    ):
        return COMPREHENSION_PRIORITY

    if (
        leaf.value in {"if", "else"}
        and leaf.parent
        and leaf.parent.type == tokens.TERNARY
    ):
        return TERNARY_PRIORITY

    if leaf.value in tokens.LOGIC_OPERATORS and leaf.parent:
        return LOGIC_PRIORITY

    return 0
