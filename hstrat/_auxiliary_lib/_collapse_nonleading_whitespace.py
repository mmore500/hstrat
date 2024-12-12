import re


def collapse_nonleading_whitespace(text: str) -> str:
    """Collapse segments of whitespace not beginning a line to a single
    space."""
    return re.sub(r"(?<=\S)[ \t]+", " ", text, flags=re.MULTILINE)
