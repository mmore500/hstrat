import math

from ._cmp import cmp


def cmp_approx(a: float, b: float) -> int:
    """
    Compare two floating-point numbers and return an integer indicating their
    relative order, considering close values equal.

    Parameters
    ----------
    a : float
        The first number to compare.
    b : float
        The second number to compare.

    Returns
    -------
    int
        1 if `a` is greater than `b`, -1 if `a` is less than `b`, 0 if `a` and
        `b` are close.

    Example
    -------
    >>> cmp_approx(1.0, 1.00000001)
    0
    >>> cmp_approx(2.0, 1.0)
    1
    >>> cmp_approx(1.0, 2.0)
    -1
    >>> cmp_approx(2.0, 2.0)
    0
    """
    return 0 if math.isclose(a, b) else cmp(a, b)
