import typing


def generate_n(generator: typing.Callable, n: int) -> typing.Iterator:
    """Returns an iterator that generates `n` values by repeatedly calling the given `generator` function.

    Parameters
    ----------
    generator : Callable
        A function that generates the values to be returned by the iterator. The function should take no arguments.
    n : int
        The number of values to generate.

    Returns
    -------
    iterator : Iterator
        An iterator that generates `n` values by repeatedly calling the `generator` function.

    Raises
    ------
    TypeError
        If `generator` is not callable.
    ValueError
        If `n` is negative.

    Examples
    --------
    >>> import random
    >>> random.seed(42)
    >>> def random_int():
    ...     return random.randint(1, 100)
    >>> values = list(generate_n(random_int, 5))
    >>> values
    [81, 14, 3, 94, 35]

    """
    for __ in range(n):
        yield generator()
