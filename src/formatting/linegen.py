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
)
from lark import Tree, Token
from dataclasses import dataclass, field

from formatting.strings import (
    normalize_string_quotes,
    is_multiline_string,
    fix_docstring,
)
from parsing.pytree import Leaf, Node
from formatting.lines import Line
from parsing import tokens
import re

T = TypeVar("T")
TT = Union[Tree, Token]
LN = Union[Leaf, Node]

IMPORTS_TYPE = {tokens.IMPORT_FROM, tokens.IMPORT_NAME}

STATEMENT_TYPES = {"FOR", "IF", "ELSE", "ELIF", "WHILE"}

SIMPLE_STATEMENTS = {
    "variable_def",
    "declaration",
    "assign",
    "aug_assign",
    "return_stmt",
    "pass_stmt",
    "break_stmt",
    "continue_stmt",
    "assert",
    "assert_with_reason",
    "assert_unreachable",
    "raise_stmt",
    "log_stmt",
    "constant_def",
    "immutable_def",
    "interface_def",
    "struct_def",
    "enum_def",
    "event_def",
    "indexed_event_arg",
    "event_member",
    "enum_member",
    "struct_member",
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
        if isinstance(node, Leaf) and node.type not in tokens.WHITESPACE:
            self.current_line.append(node)
        yield from super().visit_default(node)

    def visit_DOCSTRING(self, node: Leaf) -> Iterator[Line]:
        # don't format header docstrings
        if node.parent and node.parent.type != tokens.MODULE:
            docstring = normalize_string_quotes(node.value)

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

        yield from self.visit_default(node)

    def visit__NEWLINE(self, node: Leaf) -> Iterator[Line]:
        # if no content we can yield
        if not node.value.strip():
            yield from super().visit_default(node)

        # comments are parsed along with new lines
        # we break them down here
        comments = re.findall(r"#[^\n]*", node.value)
        if comments:
            for comment in comments:
                if node.value.strip(" \t").startswith(comment):
                    # if no new line, comment is attached to line
                    leaf = Leaf(value=comment, type=tokens.COMMENT)
                    self.current_line.append(leaf)

                else:
                    # else we have a standalone comment
                    yield from self.line()
                    leaf = Leaf(value=comment, type=tokens.STANDALONE_COMMENT)
                    self.current_line.append(leaf)

        if node.value.strip(" \t").endswith("\n\n"):
            # If user inserted multiple blank lines, we reduce to 1
            nextl = next_leaf(node)
            if nextl:
                nextl.prefix = "\n" + nextl.prefix
        yield from super().visit_default(node)

    def visit__INDENT(self, node: Leaf) -> Iterator[Line]:
        """Increase indentation level, maybe yield a line."""
        yield from self.line(+1)
        yield from self.visit_default(node)

    def visit__DEDENT(self, node: Leaf) -> Iterator[Line]:
        """Decrease indentation level, maybe yield a line."""
        # The current line might still wait for trailing comments.  At DEDENT time
        # there won't be any (they would be prefixes on the preceding NEWLINE).
        # Emit the line then.
        yield from self.line()

        # While DEDENT has no value, its prefix may contain standalone comments
        # that belong to the current indentation level.  Get 'em.
        yield from self.visit_default(node)

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

    def visit_stmt(self, node: Node, keywords: Set[str]) -> Iterator[Line]:
        """Visit a statement.
        The relevant Python language keywords for this statement are NAME leaves
        within it.
        """
        for child in node.children:
            if child.type in ({tokens.NAME} | tokens.DECLARATIONS | STATEMENT_TYPES) and child.value in keywords:  # type: ignore
                yield from self.line()

            yield from self.visit(child)

    def visit_simple_stmt(self, node: Node) -> Iterator[Line]:
        """A statement without nested statements."""
        is_body_like = node.parent and node.parent.type not in tokens.BODIES
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
        self.visit_if_stmt = partial(v, keywords={"if", "else", "elif"})
        self.visit_for_stmt = partial(v, keywords={"for", "else"})
        self.visit_function_sig = partial(v, keywords={"def"})
        for stmt in SIMPLE_STATEMENTS:
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
        self.previous_after = after
        self.previous_line = current_line
        return before, after

    def _maybe_empty_lines(self, current_line: Line) -> Tuple[int, int]:
        before = 0
        depth = current_line.depth
        while self.previous_defs and self.previous_defs[-1] >= depth:
            self.previous_defs.pop()
            before = (1 if depth else 2) - self.previous_after
        is_decorator = current_line.is_decorator
        if is_decorator or current_line.is_def:
            if not is_decorator:
                self.previous_defs.append(depth)
            if self.previous_line is None:
                # Don't insert empty lines before the first line in the file.
                return 0, 0

            if self.previous_line and self.previous_line.is_decorator:
                # Don't insert empty lines between decorators.
                return 0, 0

            # 1 space for structs, events, enums
            newlines = 1
            if is_decorator:
                # functions are all decorated and we use 2 spaces
                newlines += 1
            if current_line.depth:
                newlines -= 1
            newlines -= self.previous_after
            return newlines, 0

        if current_line.is_flow_control:
            return before, 1

        if (
            self.previous_line
            and self.previous_line.is_import
            and not current_line.is_import
            and depth == self.previous_line.depth
        ):
            return (before or 1), 0

        return before, 0


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
