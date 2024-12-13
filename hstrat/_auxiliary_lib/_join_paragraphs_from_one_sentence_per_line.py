def join_paragraphs_from_one_sentence_per_line(text: str) -> str:
    """Group lines of text into paragraphs, assuming one sentence per line.

    Strips newline after each paragraph.
    """
    return text.replace(".\n", ". ")
