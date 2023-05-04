import typing


# adapted from https://stackoverflow.com/a/22490617
def cmp(a: typing.Any, b: typing.Any) -> int:
    """Compare two objects and return an integer indicating their relative
    order.

    Parameters
    ----------
    a : Any
        The first object to be compared.
    b : Any
        The second object to be compared.

    Returns
    -------
    int
        1 if `a` is greater than `b`, -1 if `a` is less than `b`, 0 otherwise.

    Example
    -------
    >>> cmp(1, 2)
    -1
    >>> cmp(2, 1)
    1
    >>> cmp(2, 2)
    0
    """
    return bool(a > b) - bool(a < b)
