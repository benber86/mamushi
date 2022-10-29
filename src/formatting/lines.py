from dataclasses import dataclass, field
from typing import (
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Iterable,
)

from parsing import tokens
from parsing.pytree import Leaf
from formatting.whitespace import whitespace

LeafID = int
Priority = int
Depth = int
NodeType = str
COMPREHENSION_PRIORITY = 20
COMMA_PRIORITY = 10
LOGIC_PRIORITY = 5
STRING_PRIORITY = 4
COMPARATOR_PRIORITY = 3
MATH_PRIORITY = 1


@dataclass
class BracketTracker:
    depth: int = 0
    bracket_match: Dict[Tuple[Depth, NodeType], Leaf] = field(
        default_factory=dict
    )
    delimiters: Dict[LeafID, Priority] = field(default_factory=dict)
    previous: Optional[Leaf] = None

    def mark(self, leaf: Leaf) -> None:
        if leaf.type == tokens.COMMENT:
            return

        if leaf.type in tokens.CLOSING_BRACKETS:
            self.depth -= 1
            opening_bracket = self.bracket_match.pop((self.depth, leaf.type))
            leaf.opening_bracket = opening_bracket  # type: ignore
        leaf.bracket_depth = self.depth  # type: ignore
        if self.depth == 0:
            delim = is_delimiter(leaf)
            if delim:
                self.delimiters[id(leaf)] = delim
            elif self.previous is not None:
                if (
                    leaf.type == tokens.STRING
                    and self.previous.type == tokens.STRING
                ):
                    self.delimiters[id(self.previous)] = STRING_PRIORITY
                elif (
                    leaf.type == tokens.NAME
                    and leaf.value == "for"
                    and leaf.parent  # and
                    # leaf.parent.type in {syms.comp_for, syms.old_comp_for}
                ):
                    self.delimiters[id(self.previous)] = COMPREHENSION_PRIORITY
                elif (
                    leaf.type == tokens.NAME
                    and leaf.value == "if"
                    and leaf.parent  # and
                    # leaf.parent.type in {syms.comp_if, syms.old_comp_if}
                ):
                    self.delimiters[id(self.previous)] = COMPREHENSION_PRIORITY
        if leaf.type in tokens.OPENING_BRACKETS:
            self.bracket_match[
                self.depth, tokens.BRACKET_MAP[leaf.type]
            ] = leaf
            self.depth += 1
        self.previous = leaf

    def any_open_brackets(self) -> bool:
        """Returns True if there is an yet unmatched open bracket on the line."""
        return bool(self.bracket_match)

    def max_priority(self, exclude: Iterable[LeafID] = ()) -> int:
        """Returns the highest priority of a delimiter found on the line.
        Values are consistent with what `is_delimiter()` returns.
        """
        return max(v for k, v in self.delimiters.items() if k not in exclude)


@dataclass
class Line:
    depth: int = 0
    leaves: List[Leaf] = field(default_factory=list)
    comments: Dict[LeafID, Leaf] = field(default_factory=dict)
    bracket_tracker: BracketTracker = field(default_factory=BracketTracker)
    inside_brackets: bool = False

    def append(self, leaf: Leaf, preformatted: bool = False) -> None:
        has_value = leaf.value.strip()
        if not has_value:
            return

        if self.leaves and not preformatted:
            # Note: at this point leaf.prefix should be empty except for
            # imports, for which we only preserve newlines.
            leaf.prefix += whitespace(leaf)
        if self.inside_brackets or not preformatted:
            self.bracket_tracker.mark(leaf)
            self.maybe_remove_trailing_comma(leaf)
            if self.maybe_adapt_standalone_comment(leaf):
                return

        if not self.append_comment(leaf):
            self.leaves.append(leaf)

    @property
    def is_decorator(self) -> bool:
        return bool(self) and self.leaves[0].type == tokens.AT

    @property
    def is_import(self) -> bool:
        return bool(self) and is_import(self.leaves[0])

    @property
    def is_class(self) -> bool:
        return (
            bool(self)
            and self.leaves[0].type == tokens.NAME
            and self.leaves[0].value == "class"
        )

    @property
    def is_pragma(self) -> bool:
        try:
            first_leaf = self.leaves[0]
        except IndexError:
            return False
        return first_leaf.type == tokens.PRAGMA

    @property
    def is_def(self) -> bool:
        try:
            first_leaf = self.leaves[0]
        except IndexError:
            return False

        is_abi = (
            first_leaf.parent
            and first_leaf.parent.parent
            and first_leaf.parent.parent.type == tokens.INTERFACE_FUNCTION
        )
        return (first_leaf.type in tokens.DECLARATIONS) and not is_abi

    @property
    def is_flow_control(self) -> bool:
        return (
            bool(self)
            and self.leaves[0].type == tokens.NAME
            and self.leaves[0].value in tokens.FLOW_CONTROL
        )

    def maybe_remove_trailing_comma(self, closing: Leaf) -> bool:
        if not (
            self.leaves
            and self.leaves[-1].type == tokens.COMMA
            and closing.type in tokens.CLOSING_BRACKETS
        ):
            return False

        if closing.type == tokens.RSQB or closing.type == tokens.RBRACE:
            self.leaves.pop()
            return True

        # For parens let's check if it's safe to remove the comma.  If the
        # trailing one is the only one, we might mistakenly change a tuple
        # into a different type by removing the comma.
        depth = closing.bracket_depth + 1  # type: ignore
        commas = 0
        opening = closing.opening_bracket  # type: ignore
        for _opening_index, leaf in enumerate(self.leaves):
            if leaf is opening:
                break

        else:
            return False

        for leaf in self.leaves[_opening_index + 1 :]:
            if leaf is closing:
                break

            bracket_depth = leaf.bracket_depth  # type: ignore
            if bracket_depth == depth and leaf.type == tokens.COMMA:
                commas += 1
        if commas > 1:
            self.leaves.pop()
            return True

        return False

    def maybe_adapt_standalone_comment(self, comment: Leaf) -> bool:
        """Hack a standalone comment to act as a trailing comment for line splitting.
        If this line has brackets and a standalone `comment`, we need to adapt
        it to be able to still reformat the line.
        This is not perfect, the line to which the standalone comment gets
        appended will appear "too long" when splitting.
        """
        if not (
            comment.type == tokens.STANDALONE_COMMENT
            and self.bracket_tracker.any_open_brackets()
        ):
            return False

        comment.type = tokens.COMMENT
        comment.prefix = "\n" + "    " * (self.depth + 1)
        return self.append_comment(comment)

    def append_comment(self, comment: Leaf) -> bool:
        if comment.type != tokens.COMMENT:
            return False

        try:
            after = id(self.last_non_delimiter())
        except LookupError:
            comment.type = tokens.STANDALONE_COMMENT
            comment.prefix = ""
            return False

        else:
            if after in self.comments:
                self.comments[after].value += str(comment)
            else:
                self.comments[after] = comment
            return True

    def last_non_delimiter(self) -> Leaf:
        for i in range(len(self.leaves)):
            last = self.leaves[-i - 1]
            if not is_delimiter(last):
                return last

        raise LookupError("No non-delimiters found")

    def __str__(self) -> str:
        if not self:
            return "\n"

        indent = "    " * self.depth
        leaves = iter(self.leaves)
        first = next(leaves)
        res = f"{first.prefix}{indent}{first.value}"
        for leaf in leaves:
            res += str(leaf)
        for comment in self.comments.values():
            res += str(comment)
        return res + "\n"

    def __bool__(self) -> bool:
        return bool(self.leaves or self.comments)


def normalize_prefix(leaf: Leaf) -> None:
    """Leave existing extra newlines for imports.  Remove everything else."""
    if is_import(leaf):
        spl = leaf.prefix.split("#", 1)
        nl_count = spl[0].count("\n")
        if len(spl) > 1:
            # Skip one newline since it was for a standalone comment.
            nl_count -= 1
        leaf.prefix = "\n" * nl_count
        return

    leaf.prefix = ""


def is_import(leaf: Leaf) -> bool:
    """Returns True if the given leaf starts an import statement."""
    p = leaf.parent
    t = leaf.type
    v = leaf.value
    return bool(
        t == tokens.NAME
        and (
            (v == "import" and p and p.type == "import_name")
            or (v == "from" and p and p.type == "import_from")
        )
    )


def split_line(
    line: Line, line_length: int, inner: bool = False
) -> Iterator[Line]:
    """Splits a `line` into potentially many lines.
    They should fit in the allotted `line_length` but might not be able to.
    `inner` signifies that there were a pair of brackets somewhere around the
    current `line`, possibly transitively. This means we can fallback to splitting
    by delimiters if the LHS/RHS don't yield any results.
    """
    line_str = str(line).strip("\n")
    if len(line_str) <= line_length and "\n" not in line_str:
        yield line
        return

    if line.is_def:
        split_funcs = [left_hand_split]
    elif line.inside_brackets:
        split_funcs = [delimiter_split]
        if "\n" not in line_str:
            # Only attempt RHS if we don't have multiline strings or comments
            # on this line.
            split_funcs.append(right_hand_split)
    else:
        split_funcs = [right_hand_split]
    for split_func in split_funcs:
        # We are accumulating lines in `result` because we might want to abort
        # mission and return the original line in the end, or attempt a different
        # split altogether.
        result: List[Line] = []
        try:
            for split_func_l in split_func(line):
                if str(split_func_l).strip("\n") == line_str:
                    raise ValueError(
                        "Split function returned an unchanged result"
                    )

                result.extend(
                    split_line(
                        split_func_l, line_length=line_length, inner=True
                    )
                )
        except ValueError:
            continue

        else:
            yield from result
            break

    else:
        yield line


def left_hand_split(line: Line) -> Iterator[Line]:
    """Split line into many lines, starting with the first matching bracket pair.
    Note: this usually looks weird, only use this for function definitions.
    Prefer RHS otherwise.
    """
    head = Line(depth=line.depth)
    body = Line(depth=line.depth + 1, inside_brackets=True)
    tail = Line(depth=line.depth)
    tail_leaves: List[Leaf] = []
    body_leaves: List[Leaf] = []
    head_leaves: List[Leaf] = []
    current_leaves = head_leaves
    matching_bracket = None
    for leaf in line.leaves:
        if (
            current_leaves is body_leaves
            and leaf.type in tokens.CLOSING_BRACKETS
            and leaf.opening_bracket is matching_bracket  # type: ignore
        ):
            current_leaves = tail_leaves
        current_leaves.append(leaf)
        if current_leaves is head_leaves:
            if leaf.type in tokens.OPENING_BRACKETS:
                matching_bracket = leaf
                current_leaves = body_leaves
    # Since body is a new indent level, remove spurious leading whitespace.
    if body_leaves:
        normalize_prefix(body_leaves[0])
    # Build the new lines.
    for result, leaves in (
        (head, head_leaves),
        (body, body_leaves),
        (tail, tail_leaves),
    ):
        for leaf in leaves:
            result.append(leaf, preformatted=True)
            comment_after = line.comments.get(id(leaf))
            if comment_after:
                result.append(comment_after, preformatted=True)
    # Check if the split succeeded.
    tail_len = len(str(tail))
    if not body:
        if tail_len == 0:
            raise ValueError("Splitting brackets produced the same line")

        elif tail_len < 3:
            raise ValueError(
                f"Splitting brackets on an empty body to save "
                f"{tail_len} characters is not worth it"
            )

    for result in (head, body, tail):
        if result:
            yield result


def right_hand_split(line: Line) -> Iterator[Line]:
    """Split line into many lines, starting with the last matching bracket pair."""
    head = Line(depth=line.depth)
    body = Line(depth=line.depth + 1, inside_brackets=True)
    tail = Line(depth=line.depth)
    tail_leaves: List[Leaf] = []
    body_leaves: List[Leaf] = []
    head_leaves: List[Leaf] = []
    current_leaves = tail_leaves
    opening_bracket = None
    for leaf in reversed(line.leaves):
        if current_leaves is body_leaves:
            if leaf is opening_bracket:
                current_leaves = head_leaves
        current_leaves.append(leaf)
        if current_leaves is tail_leaves:
            if leaf.type in tokens.CLOSING_BRACKETS:
                opening_bracket = leaf.opening_bracket  # type: ignore
                current_leaves = body_leaves
    tail_leaves.reverse()
    body_leaves.reverse()
    head_leaves.reverse()
    # Since body is a new indent level, remove spurious leading whitespace.
    if body_leaves:
        normalize_prefix(body_leaves[0])
    # Build the new lines.
    for result, leaves in (
        (head, head_leaves),
        (body, body_leaves),
        (tail, tail_leaves),
    ):
        for leaf in leaves:
            result.append(leaf, preformatted=True)
            comment_after = line.comments.get(id(leaf))
            if comment_after:
                result.append(comment_after, preformatted=True)
    # Check if the split succeeded.
    tail_len = len(str(tail).strip("\n"))
    if not body:
        if tail_len == 0:
            raise ValueError("Splitting brackets produced the same line")

        elif tail_len < 3:
            raise ValueError(
                f"Splitting brackets on an empty body to save "
                f"{tail_len} characters is not worth it"
            )

    for result in (head, body, tail):
        if result:
            yield result


def delimiter_split(line: Line) -> Iterator[Line]:
    """Split according to delimiters of the highest priority.
    This kind of split doesn't increase indentation.
    """
    try:
        last_leaf = line.leaves[-1]
    except IndexError:
        raise ValueError("Line empty")

    delimiters = line.bracket_tracker.delimiters
    try:
        delimiter_priority = line.bracket_tracker.max_priority(
            exclude={id(last_leaf)}
        )
    except ValueError:
        raise ValueError("No delimiters found")

    current_line = Line(depth=line.depth, inside_brackets=line.inside_brackets)
    for leaf in line.leaves:
        current_line.append(leaf, preformatted=True)
        comment_after = line.comments.get(id(leaf))
        if comment_after:
            current_line.append(comment_after, preformatted=True)
        leaf_priority = delimiters.get(id(leaf))
        if leaf_priority == delimiter_priority:
            normalize_prefix(current_line.leaves[0])
            yield current_line

            current_line = Line(
                depth=line.depth, inside_brackets=line.inside_brackets
            )
    if current_line:
        if (
            delimiter_priority == COMMA_PRIORITY
            and current_line.leaves[-1].type != tokens.COMMA
        ):
            current_line.append(Leaf(tokens.COMMA, ","))
        normalize_prefix(current_line.leaves[0])
        yield current_line


def is_delimiter(leaf: Leaf) -> int:
    """Returns the priority of the `leaf` delimiter. Returns 0 if not delimiter.
    Higher numbers are higher priority.
    """
    if leaf.type == tokens.COMMA:
        return COMMA_PRIORITY

    if leaf.type == tokens.NAME and leaf.value in tokens.LOGIC_OPERATORS:
        return LOGIC_PRIORITY

    if leaf.type in tokens.COMPARATORS:
        return COMPARATOR_PRIORITY

    if (
        leaf.type in tokens.MATH_OPERATORS
        and leaf.parent
        and leaf.parent.type not in {tokens.PRODUCT}
    ):
        return MATH_PRIORITY

    return 0


def line_to_string(line: Line) -> str:
    """Returns the string representation of @line.

    WARNING: This is known to be computationally expensive.
    """
    return str(line).strip("\n")
