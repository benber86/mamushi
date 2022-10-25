from formatting.linegen import LineGenerator, EmptyLineTracker
from formatting.lines import Line, split_line
from parsing.pytree import Node


def format_tree(ast: Node, max_line_length: int = 80) -> str:
    lg = LineGenerator()
    elt = EmptyLineTracker()
    empty_line = Line()
    after = 0
    dst_contents = ""

    for current_line in lg.visit(ast):
        for _ in range(after):
            dst_contents += str(empty_line)
        before, after = elt.maybe_empty_lines(current_line)
        for _ in range(before):
            dst_contents += str(empty_line)
        for line in split_line(current_line, line_length=max_line_length):
            dst_contents += str(line)

    return dst_contents
