from formatting.linegen import LineGenerator, EmptyLineTracker
from formatting.lines import Line, split_line
from parsing.pytree import Node
from typing import List


def format_tree(ast: Node, max_line_length: int = 80) -> str:
    lg = LineGenerator()
    elt = EmptyLineTracker()
    empty_line = Line()
    comments: List[Line] = []
    after = 0
    dst_contents = ""

    for current_line in lg.visit(ast):
        for _ in range(after):
            dst_contents += str(empty_line)
        before, after = elt.maybe_empty_lines(current_line)
        for _ in range(before):
            dst_contents += str(empty_line)
        if not current_line.is_comment:
            for comment in comments:
                dst_contents += str(comment)
            comments = []
            for line in split_line(current_line, line_length=max_line_length):
                dst_contents += str(line)
        else:
            comments.append(current_line)

        for comment in comments:
            dst_contents += str(comment)
    return dst_contents
