"""
Simple formatting on strings. Further string formatting code is in trans.py.
"""

import re
import sys
from functools import lru_cache
from typing import List, Pattern, Final

from mamushi.parsing.pytree import Leaf

FIRST_NON_WHITESPACE_RE: Final = re.compile(r"\s*\t+\s*(\S)")


def has_triple_quotes(string: str) -> bool:
    """
    Returns:
        True iff @string starts with three quotation characters.
    """
    return string[:3] in {'"""', "'''"}


def is_multiline_string(leaf: Leaf) -> bool:
    """Return True if `leaf` is a multiline string that actually spans many lines."""
    return has_triple_quotes(leaf.value) and "\n" in leaf.value


def sub_twice(regex: Pattern[str], replacement: str, original: str) -> str:
    """Replace `regex` with `replacement` twice on `original`.

    This is used by string normalization to perform replaces on
    overlapping matches.
    """
    return regex.sub(replacement, regex.sub(replacement, original))


def lines_with_leading_tabs_expanded(s: str) -> List[str]:
    """
    Splits string into lines and expands only leading tabs (following the normal
    Python rules)
    """
    lines = []
    for line in s.splitlines():
        # Find the index of the first non-whitespace character after a string of
        # whitespace that includes at least one tab
        match = FIRST_NON_WHITESPACE_RE.match(line)
        if match:
            first_non_whitespace_idx = match.start(1)

            lines.append(
                line[:first_non_whitespace_idx].expandtabs()
                + line[first_non_whitespace_idx:]
            )
        else:
            lines.append(line)
    return lines


def fix_docstring(docstring: str, prefix: str) -> str:
    # https://www.python.org/dev/peps/pep-0257/#handling-docstring-indentation
    if not docstring:
        return ""
    lines = lines_with_leading_tabs_expanded(docstring)
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        last_line_idx = len(lines) - 2
        for i, line in enumerate(lines[1:]):
            stripped_line = line[indent:].rstrip()
            if stripped_line or i == last_line_idx:
                trimmed.append(prefix + stripped_line)
            else:
                trimmed.append("")
    return "\n".join(trimmed)


# Re(gex) does actually cache patterns internally but this still improves
# performance on a long list literal of strings by 5-9% since lru_cache's
# caching overhead is much lower.
@lru_cache(maxsize=64)
def _cached_compile(pattern: str) -> Pattern[str]:
    return re.compile(pattern)


def normalize_string_quotes(s: str) -> str:
    """Prefer double quotes but only if it doesn't cause more escaping.

    Adds or removes backslashes as appropriate. Doesn't parse and fix
    strings nested in f-strings.
    """

    if s[:3] == '"""':
        return s

    elif s[:3] == "'''":
        orig_quote = "'''"
        new_quote = '"""'
    elif s[0] == '"':
        orig_quote = '"'
        new_quote = "'"
    else:
        orig_quote = "'"
        new_quote = '"'
    first_quote_pos = s.find(orig_quote)
    if first_quote_pos == -1:
        return s  # There's an internal error

    prefix = s[:first_quote_pos]
    unescaped_new_quote = _cached_compile(rf"(([^\\]|^)(\\\\)*){new_quote}")
    escaped_new_quote = _cached_compile(rf"([^\\]|^)\\((?:\\\\)*){new_quote}")
    escaped_orig_quote = _cached_compile(
        rf"([^\\]|^)\\((?:\\\\)*){orig_quote}"
    )
    body = s[first_quote_pos + len(orig_quote) : -len(orig_quote)]

    # remove unnecessary escapes
    new_body = sub_twice(escaped_new_quote, rf"\1\2{new_quote}", body)
    if body != new_body:
        # Consider the string without unnecessary escapes as the original
        body = new_body
        s = f"{prefix}{orig_quote}{body}{orig_quote}"
    new_body = sub_twice(escaped_orig_quote, rf"\1\2{orig_quote}", new_body)
    new_body = sub_twice(unescaped_new_quote, rf"\1\\{new_quote}", new_body)

    if new_quote == '"""' and new_body[-1:] == '"':
        # edge case:
        new_body = new_body[:-1] + '\\"'
    orig_escape_count = body.count("\\")
    new_escape_count = new_body.count("\\")
    if new_escape_count > orig_escape_count:
        return s  # Do not introduce more escaping

    if new_escape_count == orig_escape_count and orig_quote == '"':
        return s  # Prefer double quotes

    return f"{prefix}{new_quote}{new_body}{new_quote}"


def is_pragma(string: str) -> bool:
    version = re.match(r"#\s*@version\s*(\d\.?)*", string)
    return (version is not None) and (version.group(0) == string.strip())


def remove_double_spaces(string: str) -> str:
    return re.sub(r"\s+", " ", string)
