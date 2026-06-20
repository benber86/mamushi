from mamushi.formatting.linegen import LineGenerator, EmptyLineTracker
from mamushi.formatting.lines import Line, split_line
from mamushi.parsing.pytree import Node


def _contains_fmt_off(line: str) -> bool:
    return "# fmt: off" in line or "# fmt:off" in line


def _contains_fmt_on(line: str) -> bool:
    return "# fmt: on" in line or "# fmt:on" in line


def _outermost_fmt_regions(fmt_regions):
    outermost = []
    for start, end, orig_lines in sorted(fmt_regions):
        if any(
            outer_start <= start and end <= outer_end
            for outer_start, outer_end, _ in outermost
        ):
            continue
        outermost.append((start, end, orig_lines))
    return outermost


def format_tree(ast: Node, max_line_length: int = 80, parser=None) -> str:
    lg = LineGenerator(max_line_length)
    elt = EmptyLineTracker()
    empty_line = Line()
    after = 0
    dst_contents = []

    fmt_regions = _outermost_fmt_regions(
        parser._fmt_off_regions if parser else []
    )
    fmt_region_idx = 0
    fmt_skip_depth = 0

    for current_line in lg.visit(ast):
        current_line_str = str(current_line)
        if fmt_skip_depth:
            if _contains_fmt_off(current_line_str):
                fmt_skip_depth += 1
            if _contains_fmt_on(current_line_str):
                fmt_skip_depth -= 1
            continue

        if _contains_fmt_off(current_line_str) and fmt_region_idx < len(
            fmt_regions
        ):
            _, _, orig_lines = fmt_regions[fmt_region_idx]
            fmt_region_idx += 1
            for line in orig_lines:
                dst_contents.append(line + "\n")
            fmt_skip_depth = 1
            continue

        dst_contents.append(str(empty_line) * after)
        before, after = elt.maybe_empty_lines(current_line)
        dst_contents.append(str(empty_line) * before)
        if "# nosplit" in current_line_str:
            dst_contents.append(current_line_str)
        else:
            for line in split_line(current_line, line_length=max_line_length):
                dst_contents.append(str(line))

    return "".join(dst_contents)
