# adapted from https://cs.stackexchange.com/a/65744
def parse_from_numeral_system(digits: str, alphabet: str) -> int:
    """Compute the integer value represented by string 'digits' in a custom
    base.

    Parameters
    ----------
    digits : str
        A string of digits in the custom base.
    alphabet : str
        A string of unique characters representing the digits in the custom
        base.

        The i-th character in the alphabet corresponds to the i-th digit
        in the base.

    Returns
    -------
    int
        The integer value of the number represented by the given digits in the
        custom base.

    Raises
    ------
    AssertionError
        If the alphabet contains repeated characters.

    Examples
    --------
    >>> parse_from_numeral_system('a3', '0123456789abcdef')
    163
    >>> parse_from_numeral_system('52', '01234567')
    42
    >>> parse_from_numeral_system('111', '01')
    7
    """
    assert len(alphabet) == len(set(alphabet))
    b = len(alphabet)
    n = 0
    for d in digits:
        n = b * n + alphabet.index(d)
    return n
