import shutil
import textwrap

import opytional as opyt

from ._count_leading_blanks import count_leading_blanks


def textwrap_respect_indents(text: str, ncol: int | None = None) -> str:
    """Wrap text, with wrapped lines matching leading indentation.

    Parameters
    ----------
    text : str
        The text to wrap.
    ncol : int, optional
        The maximum width of the wrapped lines.
        If not provided, defaults to the terminal width minus 4, or 60.

    Returns
    -------
    str
        The wrapped text, with wrapped lines matching leading indentation.
    """
    ncol = opyt.or_value(ncol, shutil.get_terminal_size((64, 1)).columns - 4)
    lines = [
        count_leading_blanks(line) * " " + chunk.lstrip().rstrip()
        for line in text.splitlines()
        for chunk in textwrap.wrap(
            line, drop_whitespace=False, replace_whitespace=False, width=ncol
        )
        or [""]  # prevent textwrap from gobbling empty lines
    ]
    return "\n".join(lines)
