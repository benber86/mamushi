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
from src.parsing.pytree import Leaf, Node
from src.formatting.lines import Line
from src.parsing import tokens

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

    current_line: Line = field(default_factory=Line)
    standalone_comments: List[Leaf] = field(default_factory=list)

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
        is_body_like = node.parent and node.parent.type not in {
            tokens.MODULE,
            tokens.BODY,
        }
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

    def __attrs_post_init__(self) -> None:
        """You are in a twisty little maze of passages."""
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
