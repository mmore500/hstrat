def count_leading_blanks(line: str) -> int:
    """How many leading blanks characters are there in the line?"""
    return len(line) - len(line.lstrip())
