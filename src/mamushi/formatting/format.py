from mamushi.formatting.linegen import LineGenerator, EmptyLineTracker
from mamushi.formatting.lines import Line, split_line
from mamushi.parsing.pytree import Node


def format_tree(ast: Node, max_line_length: int = 80) -> str:
    lg = LineGenerator(max_line_length)
    elt = EmptyLineTracker()
    empty_line = Line()
    after = 0
    dst_contents = []

    for current_line in lg.visit(ast):
        dst_contents.append(str(empty_line) * after)
        before, after = elt.maybe_empty_lines(current_line)
        dst_contents.append(str(empty_line) * before)
        for line in split_line(current_line, line_length=max_line_length):
            dst_contents.append(str(line))

    return "".join(dst_contents)
