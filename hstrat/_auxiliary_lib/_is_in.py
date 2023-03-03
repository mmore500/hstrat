import typing


def is_in(value: object, iterator: typing.Iterator) -> bool:
    """Check if a value is in an iterator using object identity comparison.

    Parameters
    ----------
    value : object
        The value to check for in the iterator.
    iterator : typing.Iterator
        An iterator of objects to check against the value.

    Returns
    -------
    bool
        True if the value is found in the iterator, False otherwise.

    Notes
    -----
    This function performs object identity comparison (using the `is` operator),
    not equality comparison (using the `==` operator).
    """
    for candidate in iterator:
        if value is candidate:
            return True
    return False
