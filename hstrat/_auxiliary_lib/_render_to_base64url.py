from ._render_to_numeral_system import render_to_numeral_system


def render_to_base64url(n: int) -> str:
    """Convert an integer to its digit representation in the base64url encoding.

    Parameters
    ----------
    n : int
        The non-negative integer to be converted to a base64url representation.

    Returns
    -------
    str
        A string of characters representing the base64url encoding of the given
        integer.

    Raises
    ------
    AssertionError
        If the integer is negative or if the base64url alphabet contains
        repeated characters.

    See Also
    --------
    render_to_numeral_system : A general function for converting integers to
    custom base representations.

    Notes
    -----
    The base64url encoding is specified in RFC 4648, and is similar to the
    standard base64 encoding, but replaces '+' and '/' with '-' and '_'. This
    is often used in web applications as a URL-safe encoding for binary data.

    Examples
    --------
    >>> render_to_base64url(163)
    'Cj'
    >>> render_to_base64url(42)
    'q'
    >>> render_to_base64url(7)
    'H'
    """
    base64url_alphabet = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    )
    return render_to_numeral_system(n, base64url_alphabet)
