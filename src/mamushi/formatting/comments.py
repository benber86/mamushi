import re

from mamushi.parsing.pytree import Leaf


def add_leading_space_after_hashtag(comment: str) -> str:
    """Add a space between hashtag and first character if none are there"""
    return re.sub(r"(^#)(\w)", r"# \2", comment)


def settle_prefix(comment: Leaf):
    """Puts the leading line returns in prefix"""
    stripped = comment.value.lstrip("\n")
    comment.prefix += "\n" * (len(comment.value) - len(stripped))
    comment.value = stripped
