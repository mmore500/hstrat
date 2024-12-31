import textwrap

from ._collapse_nonleading_whitespace import collapse_nonleading_whitespace
from ._join_paragraphs_from_one_sentence_per_line import (
    join_paragraphs_from_one_sentence_per_line,
)
from ._textwrap_respect_indents import textwrap_respect_indents


def format_cli_description(raw_message: str) -> str:
    """Fix whitespace to pretty-print description message on CLI, for use
    with argparse's `description` argument.

    See `hstrat.dataframe.surface_unpack_reconstruct for usage example.
    """
    message = raw_message
    message = join_paragraphs_from_one_sentence_per_line(message)
    message = collapse_nonleading_whitespace(message)
    message = textwrap_respect_indents(message)
    message = textwrap.indent(message, prefix="  ")
    return message
