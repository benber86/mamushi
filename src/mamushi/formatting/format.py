from mamushi.formatting.linegen import LineGenerator, EmptyLineTracker
from mamushi.formatting.lines import Line, split_line
from mamushi.parsing.pytree import Node


def format_tree(ast: Node, max_line_length: int = 80, parser=None) -> str:
    lg = LineGenerator(max_line_length)
    elt = EmptyLineTracker()
    empty_line = Line()
    after = 0
    dst_contents = []

    # Build region mapping for fmt: off/on regions
    fmt_regions = parser._fmt_off_regions if parser else []
    region_map = {}  # line_num -> (start, end, original_lines)
    processed_regions = set()  # Track which regions we've already emitted

    for start, end, orig_lines in fmt_regions:
        for line_num in range(start, end + 1):
            region_map[line_num] = (start, end, orig_lines)

    current_line_num = 1

    for current_line in lg.visit(ast):
        # Check if we're in a fmt-off region
        if current_line_num in region_map:
            start, end, orig_lines = region_map[current_line_num]
            region_id = (start, end)

            # Only emit the region once (when we first encounter it)
            if region_id not in processed_regions:
                for line in orig_lines:
                    dst_contents.append(line + "\n")
                processed_regions.add(region_id)

            # Skip all lines in this region (including the end line)
            if current_line_num <= end:
                current_line_num += 1
                continue

        # Normal formatting (existing logic)
        dst_contents.append(str(empty_line) * after)
        before, after = elt.maybe_empty_lines(current_line)
        dst_contents.append(str(empty_line) * before)
        if "# nosplit" in str(current_line):
            dst_contents.append(str(current_line))
        else:
            for line in split_line(current_line, line_length=max_line_length):
                dst_contents.append(str(line))

        current_line_num += 1

    return "".join(dst_contents)
