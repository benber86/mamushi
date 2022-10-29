import re


def add_leading_space_after_hashtag(comment: str) -> str:
    """Add a space between hashtag and first character if none are there"""
    return re.sub(r"(^#)(\w)", r"# \2", comment)
