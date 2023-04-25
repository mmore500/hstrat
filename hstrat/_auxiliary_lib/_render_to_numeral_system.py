# adapted from https://cs.stackexchange.com/a/65744
def render_to_numeral_system(n: int, alphabet: str) -> str:
    """Convert an integer to its digit representation in a custom base.

    Parameters
    ----------
    n : int
        The non-negative integer to be converted to a custom base
        representation.
    alphabet : str
        A string of unique characters representing the digits in the custom
        base.

        The i-th character in the alphabet corresponds to the i-th digit in the
        base.

    Returns
    -------
    str
        A string of characters representing the custom base representation of the given integer.

    Raises
    ------
    AssertionError
        If the integer is negative or if the alphabet contains repeated
        characters.

    Examples
    --------
    >>> render_to_numeral_system(163, '0123456789abcdef')
    'a3'
    >>> render_to_numeral_system(42, '01234567')
    '52'
    >>> render_to_numeral_system(7, '01')
    '111'
    """
    assert n >= 0
    assert len(alphabet) == len(set(alphabet))
    if n == 0:
        return alphabet[0]
    b = len(alphabet)
    reverse_digits = []
    while n > 0:
        reverse_digits.append(alphabet[n % b])
        n = n // b
    return "".join(reversed(reverse_digits))
