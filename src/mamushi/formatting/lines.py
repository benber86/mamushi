import itertools
import sys
from dataclasses import dataclass, field
from functools import wraps
from typing import (
    List,
    Optional,
    Collection,
    Iterator,
    Callable,
    Sequence,
    Tuple,
    TypeVar,
    Dict,
    cast,
    Set,
)
from mamushi.formatting.whitespace import whitespace
from mamushi.formatting.brackets import (
    BracketTracker,
    COMMA_PRIORITY,
    DOT_PRIORITY,
)
from mamushi.formatting.nodes import (
    ensure_visible,
    is_one_sequence_between,
    replace_child,
)
from mamushi.parsing import tokens
from mamushi.parsing.pytree import Leaf, Node


LeafID = int
T = TypeVar("T")
Index = int


class CannotTransform(Exception):
    """Base class for errors raised by Transformers."""


class CannotSplit(CannotTransform):
    """A readable split that fits the allotted line length is impossible."""


@dataclass
class Line:
    """Holds leaves and comments. Can be printed with `str(line)`."""

    depth: int = 0
    leaves: List[Leaf] = field(default_factory=list)
    # keys ordered like `leaves`
    comments: Dict[LeafID, List[Leaf]] = field(default_factory=dict)
    bracket_tracker: BracketTracker = field(default_factory=BracketTracker)
    inside_brackets: bool = False
    should_split_rhs: bool = False
    magic_trailing_comma: Optional[Leaf] = None

    def append(self, leaf: Leaf, preformatted: bool = False) -> None:
        """Add a new `leaf` to the end of the line.

        Unless `preformatted` is True, the `leaf` will receive a new consistent
        whitespace prefix and metadata applied by :class:`BracketTracker`.
        Trailing commas are maybe removed, unpacked for loop variables are
        demoted from being delimiters.

        Inline comments are put aside.
        """
        has_value = leaf.type in tokens.BRACKETS or bool(leaf.value.strip())
        if not has_value:
            return

        if self.leaves and not preformatted:
            # Note: at this point leaf.prefix should be empty except for
            # imports, for which we only preserve newlines.

            leaf.prefix += whitespace(leaf)
        if self.inside_brackets or not preformatted:
            self.bracket_tracker.mark(leaf)
            if self.has_magic_trailing_comma(leaf):
                self.magic_trailing_comma = leaf
        if not self.append_comment(leaf):
            self.leaves.append(leaf)

    def append_safe(self, leaf: Leaf, preformatted: bool = False) -> None:
        """Like :func:`append()` but disallow invalid standalone comment structure.

        Raises ValueError when any `leaf` is appended after a standalone comment
        or when a standalone comment is not the first leaf on the line.
        """
        if self.bracket_tracker.depth == 0:
            if self.is_comment:
                raise ValueError("cannot append to standalone comments")

            if self.leaves and leaf.type == tokens.STANDALONE_COMMENT:
                raise ValueError(
                    "cannot append standalone comments to a populated line"
                )

        self.append(leaf, preformatted=preformatted)

    @property
    def is_comment(self) -> bool:
        """Is this line a standalone comment?"""
        return len(self.leaves) == 1 and self.leaves[0].type in {
            tokens.STANDALONE_COMMENT,
            tokens.DOCSTRING,
        }

    @property
    def is_decorator(self) -> bool:
        """Is this line a decorator?"""
        return bool(self) and self.leaves[0].type == tokens.AT

    @property
    def is_import(self) -> bool:
        """Is this an import line?"""
        return bool(self) and is_import(self.leaves[0])

    @property
    def is_flow_control(self) -> bool:
        return (
            bool(self)
            and self.leaves[0].type == tokens.NAME
            and self.leaves[0].value in tokens.FLOW_CONTROL
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

    def contains_standalone_comments(
        self, depth_limit: int = sys.maxsize
    ) -> bool:
        """If so, needs to be split before emitting."""
        for leaf in self.leaves:
            if (
                leaf.type == tokens.STANDALONE_COMMENT
                and leaf.bracket_depth <= depth_limit
            ):
                return True

        return False

    def has_magic_trailing_comma(self, closing: Leaf) -> bool:
        """Return True if we have a magic trailing comma, that is when:
        - there's a trailing comma here
        - it's not a one-tuple
        - it's not a single-element subscript
        Additionally, if ensure_removable:
        - it's not from square bracket indexing
        (specifically, single-element square bracket indexing with
        Preview.skip_magic_trailing_comma_in_subscript)
        """
        if not (
            closing.type in tokens.CLOSING_BRACKETS
            and self.leaves
            and self.leaves[-1].type == tokens.COMMA
        ):
            return False

        if closing.type == tokens.RBRACE:
            return True

        if closing.type == tokens.RSQB:
            return True

        if self.is_import:
            return True

        if (
            closing.opening_bracket is not None
            and not is_one_sequence_between(
                closing.opening_bracket, closing, self.leaves
            )
        ):
            return True

        return False

    def append_comment(self, comment: Leaf) -> bool:
        """Add an inline or standalone comment to the line."""
        if (
            comment.type == tokens.STANDALONE_COMMENT
            and self.bracket_tracker.any_open_brackets()
        ):
            comment.prefix = ""
            return False

        if comment.type != tokens.COMMENT:
            return False

        if not self.leaves:
            comment.type = tokens.STANDALONE_COMMENT
            comment.prefix = ""
            return False

        last_leaf = self.leaves[-1]
        if (
            last_leaf.type == tokens.RPAR
            and not last_leaf.value
            and last_leaf.parent
            and len(list(last_leaf.parent.leaves())) <= 3
        ):
            # Comments on an optional parens wrapping a single leaf should belong to
            # the wrapped node except if it's a type comment. Pinning the comment like
            # this avoids unstable formatting caused by comment migration.
            if len(self.leaves) < 2:
                comment.type = tokens.STANDALONE_COMMENT
                comment.prefix = ""
                return False

            last_leaf = self.leaves[-2]
        self.comments.setdefault(id(last_leaf), []).append(comment)
        return True

    def comments_after(self, leaf: Leaf) -> List[Leaf]:
        """Generate comments that should appear directly after `leaf`."""
        return self.comments.get(id(leaf), [])

    def enumerate_with_length(
        self, reversed: bool = False
    ) -> Iterator[Tuple[Index, Leaf, int]]:
        """Return an enumeration of leaves with their length.

        Stops prematurely on standalone comments.
        """
        op = cast(
            Callable[[Sequence[Leaf]], Iterator[Tuple[Index, Leaf]]],
            enumerate_reversed if reversed else enumerate,
        )
        for index, leaf in op(self.leaves):
            length = len(leaf.prefix) + len(leaf.value)

            for comment in self.comments_after(leaf):
                length += len(comment.value)

            yield index, leaf, length

    def clone(self) -> "Line":
        return Line(
            depth=self.depth,
            inside_brackets=self.inside_brackets,
            should_split_rhs=self.should_split_rhs,
            magic_trailing_comma=self.magic_trailing_comma,
        )

    def __str__(self) -> str:
        """Render the line."""
        if not self:
            return "\n"

        indent = "    " * self.depth
        leaves = iter(self.leaves)
        first = next(leaves)
        res = f"{first.prefix}{indent}{first.value}"
        for leaf in leaves:
            res += str(leaf)
        for comment in itertools.chain.from_iterable(self.comments.values()):
            res += str(comment)

        return res + "\n"

    def __bool__(self) -> bool:
        """Return True if the line has leaves or comments."""
        return bool(self.leaves or self.comments)


def right_hand_split(
    line: Line,
    line_length: int,
    omit: Collection[LeafID] = (),
    force_optional_parentheses: bool = False,
) -> Iterator[Line]:
    """Split line into many lines, starting with the last matching bracket pair.

    If the split was by optional parentheses, attempt splitting without them, too.
    `omit` is a collection of closing bracket IDs that shouldn't be considered for
    this split.

    Note: running this function modifies `bracket_depth` on the leaves of `line`.
    """
    tail_leaves: List[Leaf] = []
    body_leaves: List[Leaf] = []
    head_leaves: List[Leaf] = []
    current_leaves = tail_leaves
    opening_bracket: Optional[Leaf] = None
    closing_bracket: Optional[Leaf] = None
    for leaf in reversed(line.leaves):
        if current_leaves is body_leaves:
            if leaf is opening_bracket:
                current_leaves = head_leaves if body_leaves else tail_leaves
        current_leaves.append(leaf)
        if current_leaves is tail_leaves:
            if leaf.type in tokens.CLOSING_BRACKETS and id(leaf) not in omit:
                opening_bracket = leaf.opening_bracket
                closing_bracket = leaf
                current_leaves = body_leaves
    if not (opening_bracket and closing_bracket and head_leaves):
        # If there is no opening or closing_bracket that means the split failed and
        # all content is in the tail.  Otherwise, if `head_leaves` are empty, it means
        # the matching `opening_bracket` wasn't available on `line` anymore.
        raise CannotSplit("No brackets found")

    tail_leaves.reverse()
    body_leaves.reverse()
    head_leaves.reverse()
    head = bracket_split_build_line(head_leaves, line, opening_bracket)
    body = bracket_split_build_line(
        body_leaves, line, opening_bracket, is_body=True
    )
    tail = bracket_split_build_line(tail_leaves, line, opening_bracket)
    bracket_split_succeeded_or_raise(head, body, tail)
    if (
        not force_optional_parentheses
        # the opening bracket is an optional paren
        and opening_bracket.type == tokens.LPAR
        and not opening_bracket.value
        # the closing bracket is an optional paren
        and closing_bracket.type == tokens.RPAR
        and not closing_bracket.value
        # it's not an import (optional parens are the only thing we can split on
        # in this case; attempting a split without them is a waste of time)
        and not line.is_import
        # there are no standalone comments in the body
        and not body.contains_standalone_comments(0)
        # and we can actually remove the parens
        and can_omit_invisible_parens(body, line_length)
    ):
        omit = {id(closing_bracket), *omit}
        try:
            yield from right_hand_split(line, line_length, omit=omit)
            return

        except CannotSplit as e:
            if not (is_line_short_enough(body, line_length=line_length)):
                raise CannotSplit(
                    "Splitting failed, body is still too long and can't be split."
                ) from e

    ensure_visible(opening_bracket)
    ensure_visible(closing_bracket)
    for result in (head, body, tail):
        if result:
            yield result


def bracket_split_build_line(
    leaves: List[Leaf],
    original: Line,
    opening_bracket: Leaf,
    *,
    is_body: bool = False,
) -> Line:
    """Return a new line with given `leaves` and respective comments from `original`.

    If `is_body` is True, the result line is one-indented inside brackets and as such
    has its first leaf's prefix normalized and a trailing comma added when expected.
    """
    result = Line(depth=original.depth)
    if is_body:
        result.inside_brackets = True
        result.depth += 1
        if leaves:
            # Ensure a trailing comma for imports and standalone function arguments, but
            # be careful not to add one after any comments or within type annotations.
            no_commas = (
                original.is_def
                and opening_bracket.value == "("
                and not any(leaf.type == tokens.COMMA for leaf in leaves)
                # In particular, don't add one within a parenthesized return annotation.
                # Unfortunately the indicator we're in a return annotation (RARROW) may
                # be defined directly in the parent node, the parent of the parent ...
                # and so on depending on how complex the return annotation is.
                # This isn't perfect and there's some false negatives but they are in
                # contexts were a comma is actually fine.
                and not any(
                    node.prev_sibling.type == tokens.RETURN_TYPE
                    for node in (
                        leaves[0].parent,
                        getattr(leaves[0].parent, "parent", None),
                    )
                    if isinstance(node, Node)
                    and isinstance(node.prev_sibling, Leaf)
                )
            )

            if original.is_import or no_commas:
                for i in range(len(leaves) - 1, -1, -1):
                    if leaves[i].type == tokens.STANDALONE_COMMENT:
                        continue

                    if leaves[i].type != tokens.COMMA:
                        new_comma = Leaf(tokens.COMMA, ",")
                        leaves.insert(i + 1, new_comma)
                    break

    # Populate the line
    for leaf in leaves:
        result.append(leaf, preformatted=True)
        for comment_after in original.comments_after(leaf):
            result.append(comment_after, preformatted=True)
    if is_body and should_split_line(result, opening_bracket):
        result.should_split_rhs = True
    return result


def should_split_line(line: Line, opening_bracket: Leaf) -> bool:
    """Should `line` be immediately split with `delimiter_split()` after RHS?"""

    if not (opening_bracket.parent and opening_bracket.value in "[{("):
        return False

    # We're essentially checking if the body is delimited by commas and there's more
    # than one of them (we're excluding the trailing comma and if the delimiter priority
    # is still commas, that means there's more).
    exclude = set()
    trailing_comma = False
    try:
        last_leaf = line.leaves[-1]
        if last_leaf.type == tokens.COMMA:
            trailing_comma = True
            exclude.add(id(last_leaf))
        max_priority = line.bracket_tracker.max_delimiter_priority(
            exclude=exclude
        )
    except (IndexError, ValueError):
        return False

    return max_priority == COMMA_PRIORITY and (
        trailing_comma
        # always explode imports
        # TODO: check for imports / mid-level ATOM
        or opening_bracket.parent.type in {tokens.ATOM}
    )


def line_to_string(line: Line) -> str:
    """Returns the string representation of @line.

    WARNING: This is known to be computationally expensive.
    """
    return str(line).strip("\n")


def is_line_short_enough(
    line: Line, line_length: int, line_str: str = ""
) -> bool:
    """Return True if `line` is no longer than `line_length`.

    Uses the provided `line_str` rendering, if any, otherwise computes a new one.
    """
    if not line_str:
        line_str = line_to_string(line)
    return (
        len(line_str) <= line_length
        and "\n" not in line_str  # multiline strings
        and not line.contains_standalone_comments()
    )


def can_omit_invisible_parens(
    line: Line,
    line_length: int,
) -> bool:
    """Does `line` have a shape safe to reformat without optional parens around it?

    Returns True for only a subset of potentially nice looking formattings but
    the point is to not return false positives that end up producing lines that
    are too long.
    """
    bt = line.bracket_tracker
    if not bt.delimiters:
        # Without delimiters the optional parentheses are useless.
        return True

    max_priority = bt.max_delimiter_priority()
    if bt.delimiter_count_with_priority(max_priority) > 1:
        # With more than one delimiter of a kind the optional parentheses read better.
        return False

    if max_priority == DOT_PRIORITY:
        # A single stranded method call doesn't require optional parentheses.
        return True

    assert len(line.leaves) >= 2, "Stranded delimiter"

    # With a single delimiter, omit if the expression starts or ends with
    # a bracket.
    first = line.leaves[0]
    second = line.leaves[1]
    if (
        first.type in tokens.OPENING_BRACKETS
        and second.type not in tokens.CLOSING_BRACKETS
    ):
        if _can_omit_opening_paren(line, first=first, line_length=line_length):
            return True

        # Note: we are not returning False here because a line might have *both*
        # a leading opening bracket and a trailing closing bracket.  If the
        # opening bracket doesn't match our rule, maybe the closing will.

    penultimate = line.leaves[-2]
    last = line.leaves[-1]

    if last.type == tokens.RPAR or last.type == tokens.RBRACE:
        if penultimate.type in tokens.OPENING_BRACKETS:
            # Empty brackets don't help.
            return False

        if _can_omit_closing_paren(line, last=last, line_length=line_length):
            return True

    return False


def _can_omit_opening_paren(
    line: Line, *, first: Leaf, line_length: int
) -> bool:
    """See `can_omit_invisible_parens`."""
    remainder = False
    length = 4 * line.depth
    _index = -1
    for _index, leaf, leaf_length in line.enumerate_with_length():
        if (
            leaf.type in tokens.CLOSING_BRACKETS
            and leaf.opening_bracket is first
        ):
            remainder = True
        if remainder:
            length += leaf_length
            if length > line_length:
                break

            if leaf.type in tokens.OPENING_BRACKETS:
                # There are brackets we can further split on.
                remainder = False

    else:
        # checked the entire string and line length wasn't exceeded
        if len(line.leaves) == _index + 1:
            return True

    return False


def _can_omit_closing_paren(
    line: Line, *, last: Leaf, line_length: int
) -> bool:
    """See `can_omit_invisible_parens`."""
    length = 4 * line.depth
    seen_other_brackets = False
    for _index, leaf, leaf_length in line.enumerate_with_length():
        length += leaf_length
        if leaf is last.opening_bracket:
            if seen_other_brackets or length <= line_length:
                return True

        elif leaf.type in tokens.OPENING_BRACKETS:
            # There are brackets we can further split on.
            seen_other_brackets = True

    return False


def bracket_split_succeeded_or_raise(
    head: Line, body: Line, tail: Line
) -> None:
    """Raise :exc:`CannotSplit` if the last left- or right-hand split failed.

    Do nothing otherwise.

    A left- or right-hand split is based on a pair of brackets. Content before
    (and including) the opening bracket is left on one line, content inside the
    brackets is put on a separate line, and finally content starting with and
    following the closing bracket is put on a separate line.

    Those are called `head`, `body`, and `tail`, respectively. If the split
    produced the same line (all content in `head`) or ended up with an empty `body`
    and the `tail` is just the closing bracket, then it's considered failed.
    """
    tail_len = len(str(tail).strip())
    if not body:
        if tail_len == 0:
            raise CannotSplit("Splitting brackets produced the same line")

        elif tail_len < 3:
            raise CannotSplit(
                f"Splitting brackets on an empty body to save {tail_len} characters is"
                " not worth it"
            )


def is_import(leaf: Leaf) -> bool:
    """Returns True if the given leaf starts an import statement."""
    p = leaf.parent
    t = leaf.type
    v = leaf.value
    return bool(
        t in {tokens.IMPORT_FROM, tokens.IMPORT}
        and (
            (v == "import" and p and p.type == "import")
            or (v == "from" and p and p.type == "import")
        )
    )


def enumerate_reversed(sequence: Sequence[T]) -> Iterator[Tuple[Index, T]]:
    """Like `reversed(enumerate(sequence))` if that were possible."""
    index = len(sequence) - 1
    for element in reversed(sequence):
        yield (index, element)
        index -= 1


def left_hand_split(
    line: Line, force_optional_parentheses: bool = False
) -> Iterator[Line]:
    """Split line into many lines, starting with the first matching bracket pair.

    Note: this usually looks weird, only use this for function definitions.
    Prefer RHS otherwise.  This is why this function is not symmetrical with
    :func:`right_hand_split` which also handles optional parentheses.
    """
    tail_leaves: List[Leaf] = []
    body_leaves: List[Leaf] = []
    head_leaves: List[Leaf] = []
    current_leaves = head_leaves
    matching_bracket: Optional[Leaf] = None
    for leaf in line.leaves:
        if (
            current_leaves is body_leaves
            and leaf.type in tokens.CLOSING_BRACKETS
            and leaf.opening_bracket is matching_bracket
            and isinstance(matching_bracket, Leaf)
        ):
            ensure_visible(leaf)
            ensure_visible(matching_bracket)
            current_leaves = tail_leaves if body_leaves else head_leaves
        current_leaves.append(leaf)
        if current_leaves is head_leaves:
            if leaf.type in tokens.OPENING_BRACKETS:
                matching_bracket = leaf
                current_leaves = body_leaves
    if not matching_bracket:
        raise CannotSplit("No brackets found")

    head = bracket_split_build_line(head_leaves, line, matching_bracket)
    body = bracket_split_build_line(
        body_leaves, line, matching_bracket, is_body=True
    )
    tail = bracket_split_build_line(tail_leaves, line, matching_bracket)
    bracket_split_succeeded_or_raise(head, body, tail)
    for result in (head, body, tail):
        if result:
            yield result


def normalize_prefix(leaf: Leaf, *, inside_brackets: bool) -> None:
    """Leave existing extra newlines if not `inside_brackets`. Remove everything
    else.

    Note: don't use backslashes for formatting or you'll lose your voting rights.
    """
    if not inside_brackets:
        spl = leaf.prefix.split("#")
        if "\\" not in spl[0]:
            nl_count = spl[-1].count("\n")
            if len(spl) > 1:
                nl_count -= 1
            leaf.prefix = "\n" * nl_count
            return

    leaf.prefix = ""


def dont_increase_indentation(split_func: Callable):
    """Normalize prefix of the first leaf in every line returned by `split_func`.

    This is a decorator over relevant split functions.
    """

    @wraps(split_func)
    def split_wrapper(
        line: Line, force_optional_parentheses: bool = False
    ) -> Iterator[Line]:
        for split_line in split_func(line):
            normalize_prefix(split_line.leaves[0], inside_brackets=True)
            yield split_line

    return split_wrapper


@dont_increase_indentation
def delimiter_split(
    line: Line, force_optional_parentheses: bool = False
) -> Iterator[Line]:
    """Split according to delimiters of the highest priority.

    If the appropriate Features are given, the split will add trailing commas
    also in function signatures and calls that contain `*` and `**`.
    """
    try:
        last_leaf = line.leaves[-1]
    except IndexError:
        raise CannotSplit("Line empty") from None

    bt = line.bracket_tracker
    try:
        delimiter_priority = bt.max_delimiter_priority(exclude={id(last_leaf)})
    except ValueError:
        raise CannotSplit("No delimiters found") from None

    if delimiter_priority == DOT_PRIORITY:
        if bt.delimiter_count_with_priority(delimiter_priority) == 1:
            raise CannotSplit(
                "Splitting a single attribute from its owner looks wrong"
            )

    current_line = Line(depth=line.depth, inside_brackets=line.inside_brackets)

    def append_to_line(leaf: Leaf) -> Iterator[Line]:
        """Append `leaf` to current line or to new line if appending impossible."""
        nonlocal current_line
        try:
            current_line.append_safe(leaf, preformatted=True)
        except ValueError:
            yield current_line

            current_line = Line(
                depth=line.depth, inside_brackets=line.inside_brackets
            )
            current_line.append(leaf)

    for leaf in line.leaves:
        yield from append_to_line(leaf)

        for comment_after in line.comments_after(leaf):
            yield from append_to_line(comment_after)

        leaf_priority = bt.delimiters.get(id(leaf))
        if leaf_priority == delimiter_priority:
            yield current_line

            current_line = Line(
                depth=line.depth, inside_brackets=line.inside_brackets
            )
    if current_line:
        if (
            delimiter_priority == COMMA_PRIORITY
            and current_line.leaves[-1].type != tokens.COMMA
            and current_line.leaves[-1].type != tokens.STANDALONE_COMMENT
        ):
            new_comma = Leaf(tokens.COMMA, ",")
            current_line.append(new_comma)
        yield current_line


def split_line(
    line: Line,
    line_length: int,
    inner: bool = False,
    force_optional_parentheses: bool = False,
) -> Iterator[Line]:
    """Splits a `line` into potentially many lines.
    They should fit in the allotted `line_length` but might not be able to.
    `inner` signifies that there were a pair of brackets somewhere around the
    current `line`, possibly transitively. This means we can fallback to splitting
    by delimiters if the LHS/RHS don't yield any results.
    """
    if line.is_comment:
        yield line
        return

    line_str = str(line).strip("\n")
    if (
        not line.should_split_rhs
        and not line.magic_trailing_comma
        and (is_line_short_enough(line, line_length, line_str=line_str))
        and not (line.inside_brackets and line.contains_standalone_comments())
    ):
        transformers = []

    elif line.is_def:
        transformers = [left_hand_split]
    else:

        def _rhs(
            self: object, line: Line, force_optional_parentheses=False
        ) -> Iterator[Line]:
            """Wraps calls to `right_hand_split`.

            The calls increasingly `omit` right-hand trailers (bracket pairs with
            content), meaning the trailers get glued together to split on another
            bracket pair instead.
            """
            for omit in generate_trailers_to_omit(line, line_length):
                lines = list(
                    right_hand_split(
                        line,
                        line_length,
                        omit=omit,
                        force_optional_parentheses=force_optional_parentheses,
                    )
                )
                # Note: this check is only able to figure out if the first line of the
                # *current* transformation fits in the line length.  This is true only
                # for simple cases.  All others require running more transforms via
                # `transform_line()`.  This check doesn't know if those would succeed.
                if is_line_short_enough(lines[0], line_length=line_length):
                    yield from lines
                    return

            # All splits failed, best effort split with no omits.
            # This mostly happens to multiline strings that are by definition
            # reported as not fitting a single line, as well as lines that contain
            # trailing commas (those have to be exploded).
            yield from right_hand_split(
                line,
                line_length=line_length,
                force_optional_parentheses=force_optional_parentheses,
            )

        # HACK: nested functions (like _rhs) compiled by mypyc don't retain their
        # __name__ attribute which is needed in `run_transformer` further down.
        # Unfortunately a nested class breaks mypyc too. So a class must be created
        # via type ... https://github.com/mypyc/mypyc/issues/884
        rhs = type("rhs", (), {"__call__": _rhs})()

        if line.inside_brackets:
            transformers = [delimiter_split, rhs]
        else:
            transformers = [rhs]

    transformers.append(hug_power_op)

    for transform in transformers:
        # We are accumulating lines in `result` because we might want to abort
        # mission and return the original line in the end, or attempt a different
        # split altogether.
        try:
            result = run_transformer(
                line,
                transform,
                line_length=line_length,
                line_str=line_str,
                force_optional_parentheses=force_optional_parentheses,
            )
        except CannotTransform:
            continue
        else:
            yield from result
            break

    else:
        yield line


def generate_trailers_to_omit(
    line: Line, line_length: int
) -> Iterator[Set[LeafID]]:
    """Generate sets of closing bracket IDs that should be omitted in a RHS.

    Brackets can be omitted if the entire trailer up to and including
    a preceding closing bracket fits in one line.

    Yielded sets are cumulative (contain results of previous yields, too).  First
    set is empty, unless the line should explode, in which case bracket pairs until
    the one that needs to explode are omitted.
    """

    omit: Set[LeafID] = set()
    if not line.magic_trailing_comma:
        yield omit

    length = 4 * line.depth
    opening_bracket: Optional[Leaf] = None
    closing_bracket: Optional[Leaf] = None
    inner_brackets: Set[LeafID] = set()
    for index, leaf, leaf_length in line.enumerate_with_length(reversed=True):
        length += leaf_length
        if length > line_length:
            break

        has_inline_comment = leaf_length > len(leaf.value) + len(leaf.prefix)
        if leaf.type == tokens.STANDALONE_COMMENT or has_inline_comment:
            break

        if opening_bracket:
            if leaf is opening_bracket:
                opening_bracket = None
            elif leaf.type in tokens.CLOSING_BRACKETS:
                prev = line.leaves[index - 1] if index > 0 else None
                if (
                    prev
                    and prev.type == tokens.COMMA
                    and leaf.opening_bracket is not None
                    and not is_one_sequence_between(
                        leaf.opening_bracket, leaf, line.leaves
                    )
                ):
                    # Never omit bracket pairs with trailing commas.
                    # We need to explode on those.
                    break

                inner_brackets.add(id(leaf))
        elif leaf.type in tokens.CLOSING_BRACKETS:
            prev = line.leaves[index - 1] if index > 0 else None
            if prev and prev.type in tokens.OPENING_BRACKETS:
                # Empty brackets would fail a split so treat them as "inner"
                # brackets (e.g. only add them to the `omit` set if another
                # pair of brackets was good enough.
                inner_brackets.add(id(leaf))
                continue

            if closing_bracket:
                omit.add(id(closing_bracket))
                omit.update(inner_brackets)
                inner_brackets.clear()
                yield omit

            if (
                prev
                and prev.type == tokens.COMMA
                and leaf.opening_bracket is not None
                and not is_one_sequence_between(
                    leaf.opening_bracket, leaf, line.leaves
                )
            ):
                # Never omit bracket pairs with trailing commas.
                # We need to explode on those.
                break

            if leaf.value:
                opening_bracket = leaf.opening_bracket
                closing_bracket = leaf


def run_transformer(
    line: Line,
    transform: Callable[[Line, bool], Iterator[Line]],
    line_length: int = 80,
    line_str: str = "",
    force_optional_parentheses=False,
) -> List[Line]:
    if not line_str:
        line_str = line_to_string(line)
    result: List[Line] = []
    for transformed_line in transform(line, force_optional_parentheses):
        if str(transformed_line).strip("\n") == line_str:
            raise CannotTransform(
                "Line transformer returned an unchanged result"
            )

        result.extend(
            split_line(
                transformed_line,
                line_length,
                force_optional_parentheses=force_optional_parentheses,
            )
        )

    if (
        transform.__class__.__name__ != "rhs"
        or not line.bracket_tracker.invisible
        or any(bracket.value for bracket in line.bracket_tracker.invisible)
        or is_line_short_enough(result[0], line_length=line_length)
        # If any leaves have no parents (which _can_ occur since
        # `transform(line)` potentially destroys the line's underlying node
        # structure), then we can't proceed. Doing so would cause the below
        # call to `append_leaves()` to fail.
        or any(leaf.parent is None for leaf in line.leaves)
    ):
        return result

    line_copy = line.clone()
    append_leaves(line_copy, line, line.leaves)
    second_opinion = run_transformer(
        line_copy,
        transform,
        line_str=line_str,
        force_optional_parentheses=True,
    )
    if all(
        is_line_short_enough(ln, line_length=line_length)
        for ln in second_opinion
    ):
        result = second_opinion
    return result


def append_leaves(
    new_line: Line,
    old_line: Line,
    leaves: List[Leaf],
    preformatted: bool = False,
) -> None:
    """
    Append leaves (taken from @old_line) to @new_line, making sure to fix the
    underlying Node structure where appropriate.

    All of the leaves in @leaves are duplicated. The duplicates are then
    appended to @new_line and used to replace their originals in the underlying
    Node structure. Any comments attached to the old leaves are reattached to
    the new leaves.

    Pre-conditions:
        set(@leaves) is a subset of set(@old_line.leaves).
    """
    for old_leaf in leaves:
        new_leaf = Leaf(old_leaf.type, old_leaf.value)
        replace_child(old_leaf, new_leaf)
        new_line.append(new_leaf, preformatted=preformatted)

        for comment_leaf in old_line.comments_after(old_leaf):
            new_line.append(comment_leaf, preformatted=True)


def hug_power_op(
    line: Line, force_optional_parentheses: bool = False
) -> Iterator[Line]:
    """A transformer which normalizes spacing around power operators."""

    # Performance optimization to avoid unnecessary Leaf clones and other ops.
    for leaf in line.leaves:
        if leaf.type == tokens.DOUBLESTAR:
            break
    else:
        raise CannotTransform("No doublestar token was found in the line.")

    new_line = line.clone()
    should_hug = False
    for idx, leaf in enumerate(line.leaves):
        new_leaf = leaf.clone()
        if should_hug:
            new_leaf.prefix = ""
            should_hug = False

        should_hug = (0 < idx < len(line.leaves) - 1) and (
            leaf.type == tokens.DOUBLESTAR
            # we don't want to hug if we're in x **= y
            and bool(
                leaf.parent
                and leaf.parent.parent
                and leaf.parent.parent.type != tokens.AUG_ASSIGN
            )
        )
        if should_hug:
            new_leaf.prefix = ""

        # We have to be careful to make a new line properly:
        # - bracket related metadata must be maintained (handled by Line.append)
        # - comments need to copied over, updating the leaf IDs they're attached to
        new_line.append(new_leaf, preformatted=True)
        for comment_leaf in line.comments_after(leaf):
            new_line.append(comment_leaf, preformatted=True)

    yield new_line
