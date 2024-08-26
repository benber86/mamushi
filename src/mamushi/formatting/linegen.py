from functools import partial
from typing import (
    Generic,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
)
from lark import Tree, Token
from dataclasses import dataclass, field

from mamushi.formatting.comments import (
    add_leading_space_after_hashtag,
    settle_prefix,
)
from mamushi.formatting.nodes import (
    wrap_in_parentheses,
    is_atom_with_invisible_parens,
    ensure_visible,
)
from mamushi.formatting.strings import (
    normalize_string_quotes,
    is_multiline_string,
    fix_docstring,
    is_pragma,
)
from mamushi.parsing.pytree import Leaf, Node
from mamushi.formatting.lines import Line
from mamushi.parsing.tokens import SIMPLE_STATEMENTS, ASSIGNMENTS_SIGNS
from mamushi.parsing import tokens
import re

T = TypeVar("T")
TT = Union[Tree, Token]
LN = Union[Leaf, Node]

IMPORTS_TYPE = {tokens.IMPORT_FROM, tokens.IMPORT_NAME}

STATEMENT_TYPES = {
    tokens.FOR,
    tokens.IF,
    tokens.ELSE,
    tokens.ELIF,
    tokens.ASSERT_TOKEN,
}

ASSIGNMENTS = {
    tokens.DECLARATION,
    tokens.CONSTANT_DEF,
    tokens.ASSIGN,
    tokens.AUG_ASSIGN,
}


class Visitor(Generic[T]):
    def visit(self, node: LN) -> Iterator[T]:
        yield from getattr(self, f"visit_{node.type}", self.visit_default)(
            node
        )

    def visit_default(self, node: LN) -> Iterator[T]:
        if isinstance(node, Node):
            for child in node.children:
                yield from self.visit(child)


@dataclass
class LineGenerator(Visitor[Line]):
    """Generates reformatted Line objects.  Empty lines are not emitted.
    Note: destroys the tree it's visiting by mutating prefixes of its leaves
    in ways that will no longer stringify to valid Python code on the tree.
    """

    def __init__(self, line_length: int = 80) -> None:
        self.current_line: Line
        self.__post_init__()
        self.line_length = line_length

    def line(self, indent: int = 0) -> Iterator[Line]:
        """Generate a line.
        If the line is empty, only emit if it makes sense.
        If the line is too long, split it first and then generate.
        If any lines were generated, set up a new current_line.
        """
        if not self.current_line:
            self.current_line.depth += indent
            return  # Line is empty, don't emit. Creating a new one unnecessary.

        complete_line = self.current_line
        self.current_line = Line(depth=complete_line.depth + indent)
        yield complete_line

    def visit_default(self, node: LN) -> Iterator[Line]:
        if isinstance(node, Leaf):
            if node.type == tokens.STRING:
                node.value = normalize_string_quotes(node.value)
            if node.type not in tokens.WHITESPACE:
                self.current_line.append(node)
            if (
                node.type == tokens.STANDALONE_COMMENT
                and not self.current_line.bracket_tracker.any_open_brackets()
            ):
                yield from self.line()
        yield from super().visit_default(node)

    def visit_external_call(self, node: Node) -> Iterator[Line]:
        yield from self.visit_call(node)

    def visit_DOCSTRING(self, node: Leaf) -> Iterator[Line]:
        # ensure single/double quote consistency
        docstring = normalize_string_quotes(node.value)
        # don't further format header docstrings
        if node.parent and node.parent.type != tokens.MODULE:
            quote_char = docstring[0]
            # A natural way to remove the outer quotes is to do:
            #   docstring = docstring.strip(quote_char)
            # but that breaks on """""x""" (which is '""x').
            # So we actually need to remove the first character and the next two
            # characters but only if they are the same as the first.
            quote_len = 1 if docstring[1] != quote_char else 3
            docstring = docstring[quote_len:-quote_len]
            docstring_started_empty = not docstring
            indent = " " * 4 * self.current_line.depth

            if is_multiline_string(node):
                docstring = fix_docstring(docstring, indent)
            else:
                docstring = docstring.strip()

            if docstring:
                # Add some padding if the docstring starts / ends with a quote mark.
                if docstring[0] == quote_char:
                    docstring = " " + docstring
                if docstring[-1] == quote_char:
                    docstring += " "
                if docstring[-1] == "\\":
                    backslash_count = len(docstring) - len(
                        docstring.rstrip("\\")
                    )
                    if backslash_count % 2:
                        # Odd number of tailing backslashes, add some padding to
                        # avoid escaping the closing string quote.
                        docstring += " "
            elif not docstring_started_empty:
                docstring = " "

            # We could enforce triple quotes at this point.
            quote = quote_char * quote_len
            if quote_len == 3:
                # We need to find the length of the last line of the docstring
                # to find if we can add the closing quotes to the line without
                # exceeding the maximum line length.
                # If docstring is one line, then we need to add the length
                # of the indent, prefix, and starting quotes. Ending quotes are
                # handled later.
                lines = docstring.splitlines()
                last_line_length = len(lines[-1]) if docstring else 0

                if len(lines) == 1:
                    last_line_length += len(indent) + quote_len

                # If adding closing quotes would cause the last line to exceed
                # the maximum line length then put a line break before the
                # closing quotes
                if last_line_length + quote_len > self.line_length:
                    node.value = quote + docstring + "\n" + indent + quote
                else:
                    node.value = quote + docstring + quote
            else:
                node.value = quote + docstring + quote
        else:
            node.value = docstring
        yield from self.visit_default(node)

    def visit_COMMENT(self, node: Leaf) -> Iterator[Line]:
        any_open_brackets = (
            self.current_line.bracket_tracker.any_open_brackets()
        )
        node.value = add_leading_space_after_hashtag(node.value)
        settle_prefix(node)
        if is_pragma(node.value):
            node.type = tokens.PRAGMA
        self.current_line.append(node)
        if not any_open_brackets:
            # regular trailing comment
            yield from self.line()
        yield from super().visit_default(node)

    def visit_STANDALONE_COMMENT(self, node: Leaf) -> Iterator[Line]:
        node.value = re.sub(r"\n\n+", "\n\n", node.value)
        node.value = add_leading_space_after_hashtag(node.value)
        settle_prefix(node)
        if not self.current_line.bracket_tracker.any_open_brackets():
            yield from self.line()
        yield from self.visit_default(node)

    def visit__NEWLINE(self, node: Leaf) -> Iterator[Line]:
        nextl = next_leaf_add_newline(node)
        if nextl:
            nextl.prefix = "\n" + nextl.prefix
        else:
            yield from self.line()
        yield from super().visit_default(node)

    def visit__INDENT(self, node: Leaf) -> Iterator[Line]:
        """Increase indentation level, maybe yield a line."""
        yield from self.line(+1)
        yield from self.visit_default(node)

    def visit__DEDENT(self, node: Leaf) -> Iterator[Line]:
        """Decrease indentation level, maybe yield a line."""
        nextl = next_leaf_add_newline(node)
        if nextl:
            nextl.prefix = "\n" + nextl.prefix
        yield from self.line()

        # Finally, emit the dedent.
        yield from self.line(-1)

    def visit_body(self, node: Node) -> Iterator[Line]:
        yield from self.visit_default(node)

    def visit_call(self, node: Node) -> Iterator[Line]:
        """
        Handles calls depending on whether they're a standalone statement
        or part of a compound statement
        """
        if not node.parent or node.parent and node.parent.type == tokens.BODY:
            yield from self.line()
            yield from self.visit_default(node)
        else:
            for child in node.children:
                yield from self.visit(child)

    def visit_import(self, node: Node) -> Iterator[Line]:
        """Handles different import syntax"""
        for child in node.children:
            if child.type in IMPORTS_TYPE and child.prev_sibling is None:
                yield from self.line()
            yield from self.visit(child)

    def visit_stmt(
        self, node: Node, keywords: Set[str], parens: Set[str]
    ) -> Iterator[Line]:
        """Visit a statement."""
        normalize_invisible_parens(node, parens_after=parens)
        for child in node.children:
            if child.type in ({tokens.NAME} | tokens.DECLARATIONS | STATEMENT_TYPES) and child.value in keywords:  # type: ignore
                yield from self.line()

            yield from self.visit(child)

    def visit_simple_stmt(self, node: Node) -> Iterator[Line]:
        """A statement without nested statements."""
        if node.type in ASSIGNMENTS:
            normalize_invisible_parens(node, parens_after=ASSIGNMENTS_SIGNS)
        elif node.type in tokens.ASSERTS:
            normalize_invisible_parens(node, parens_after={"assert", ","})
        elif node.type == tokens.RETURN_STMT:
            normalize_invisible_parens(node, parens_after={"return"})

        is_body_like = node.parent and (
            # TODO: handle this more cleanly
            node.parent.type not in tokens.BODIES
            # for single line body stmts
            or (
                node.parent.type == tokens.BODY
                and node.type in SIMPLE_STATEMENTS
                and not node.prev_sibling
            )
        )
        if is_body_like:
            yield from self.line(+1)
            yield from self.visit_default(node)
            yield from self.line(-1)

        else:
            yield from self.line()
            yield from self.visit_default(node)

    def visit_decorators(self, node: Node) -> Iterator[Line]:
        """Visit decorators."""
        for child in node.children:
            yield from self.line()
            yield from self.visit(child)

    def __post_init__(self) -> None:
        """You are in a twisty little maze of passages."""
        self.current_line = Line()
        v = self.visit_stmt
        self.visit_if_stmt = partial(
            v, keywords={"if", "else", "elif"}, parens={"if", "elif"}
        )
        self.visit_for_stmt = partial(v, keywords={"for", "else"}, parens={""})
        self.visit_function_sig = partial(v, keywords={"def"}, parens=set())

        for stmt in SIMPLE_STATEMENTS | ASSIGNMENTS:
            self.__setattr__(f"visit_{stmt}", self.visit_simple_stmt)


@dataclass
class EmptyLineTracker:
    """Provides a stateful method that returns the number of potential extra
    empty lines needed before and after the currently processed line.
    Note: this tracker works on lines that haven't been split yet.
    """

    previous_line: Optional[Line] = None
    previous_after: int = 0
    previous_defs: List[int] = field(default_factory=list)

    def maybe_empty_lines(self, current_line: Line) -> Tuple[int, int]:
        """Returns the number of extra empty lines before and after the `current_line`.
        This is for separating `def`, `async def` and `class` with extra empty lines
        (two on module-level), as well as providing an extra empty line after flow
        control keywords to make them more prominent.
        """
        before, after = self._maybe_empty_lines(current_line)
        before = (
            0 if self.previous_line is None else before - self.previous_after
        )
        self.previous_after = after
        self.previous_line = current_line
        return before, after

    def _maybe_empty_lines(self, current_line: Line) -> Tuple[int, int]:
        max_allowed = 2
        if current_line.leaves:
            # Consume the first leaf's extra newlines.
            first_leaf = current_line.leaves[0]
            before = first_leaf.prefix.count("\n")
            before = min(before, max_allowed)
            first_leaf.prefix = ""
        else:
            before = 0
        depth = current_line.depth
        while self.previous_defs and self.previous_defs[-1] >= depth:
            self.previous_defs.pop()
            before = (1 if depth else 2) - self.previous_after
        is_decorator = current_line.is_decorator
        if is_decorator or current_line.is_def:
            return self._maybe_empty_lines_for_class_or_def(
                current_line, before
            )

        if current_line.is_flow_control:
            return before, 1

        if current_line.is_pragma:
            return 0, 1

        if (
            self.previous_line
            and self.previous_line.is_import
            and not current_line.is_import
            and depth == self.previous_line.depth
        ):
            return (before or 1), 0

        return before, 0

    def _maybe_empty_lines_for_class_or_def(
        self, current_line: Line, before: int
    ) -> Tuple[int, int]:
        if not current_line.is_decorator:
            self.previous_defs.append(current_line.depth)
        if self.previous_line is None:
            # Don't insert empty lines before the first line in the file.
            return 0, 0

        if self.previous_line.is_decorator:
            return 0, 0

        if self.previous_line.depth < current_line.depth and (
            self.previous_line.is_def
        ):
            return 0, 0

        if (
            self.previous_line.is_comment
            and self.previous_line.depth == current_line.depth
            and before == 0
        ):
            return 0, 0

        else:
            newlines = 1 if current_line.depth else 2
        return newlines, 0


def next_leaf(node: Optional[LN]) -> Optional[Leaf]:
    """Return the first leaf that precedes `node`, if any."""
    while node:
        res = node.next_sibling
        if res:
            if isinstance(res, Leaf):
                return res

            try:
                return list(res.leaves())[0]

            except IndexError:
                return None

        node = node.parent
    return None


def normalize_invisible_parens(
    node: Node,
    parens_after: Set[str],
) -> None:
    """Make existing optional parentheses invisible or create new ones.

    `parens_after` is a set of string leaf values immediately after which parens
    should be put.

    Standardizes on visible parentheses for single-element tuples, and keeps
    existing visible parentheses for other tuples and generator expressions.
    """

    check_lpar = False
    for index, child in enumerate(list(node.children)):
        # Add parentheses around tuple assignments on lhs.
        if (
            index == 0
            and isinstance(child, Node)
            and child.type == tokens.MULTIPLE_ASSIGN
        ):
            check_lpar = True

        if check_lpar:
            if child.type == tokens.COND_EXEC:
                first_child = child.children[0]
                if (
                    isinstance(first_child, Node)
                    and isinstance(child, Node)
                    and maybe_make_parens_invisible_in_atom(
                        child.children[0],
                        parent=child,
                    )
                ):
                    wrap_in_parentheses(child, first_child, visible=False)

            elif not (isinstance(child, Leaf)):
                wrap_in_parentheses(node, child, visible=False)

        check_lpar = isinstance(child, Leaf) and (child.value in parens_after)


def maybe_make_parens_invisible_in_atom(
    node: LN,
    parent: LN,
    remove_brackets_around_comma: bool = False,
) -> bool:
    """If it's safe, make the parens in the atom `node` invisible, recursively.
    Additionally, remove repeated, adjacent invisible parens from the atom `node`
    as they are redundant.

    Returns whether the node should itself be wrapped in invisible parentheses.
    """

    first = node.children[0]
    last = node.children[-1]
    if (
        isinstance(first, Leaf)
        and first.type == tokens.LPAR
        and first.value == "("
        and isinstance(last, Leaf)
        and last.type == tokens.RPAR
        and last.value == ")"
    ):
        middle = node.children[1]
        # make parentheses invisible
        first.value = ""
        last.value = ""
        maybe_make_parens_invisible_in_atom(
            middle,
            parent=parent,
            remove_brackets_around_comma=remove_brackets_around_comma,
        )

        if is_atom_with_invisible_parens(middle):
            # Strip the invisible parens from `middle` by replacing
            # it with the child in-between the invisible parens
            middle.replace(middle.children[1])

        return False

    return True


def get_next_non_whitespace_leaf(node: Leaf) -> Optional[Leaf]:
    nextl = next_leaf(node)
    while nextl and nextl.type in tokens.WHITESPACE:
        nextl = next_leaf(nextl)
    return nextl


def next_leaf_add_newline(node: Leaf) -> Optional[Leaf]:
    if node.value.strip(" \t").endswith("\n\n"):
        # If user inserted multiple blank lines, we reduce to 1
        return get_next_non_whitespace_leaf(node)
    return None
