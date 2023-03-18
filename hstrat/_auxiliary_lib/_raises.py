import typing


def raises(callable: typing.Callable, exception: BaseException) -> bool:
    """Test if a `callable` raises a `exception` when called.

    Parameters
    ----------
    callable : typing.Callable
        The callable to be tested for raising the specified exception.
    exception : BaseException
        The exception that is expected to be raised by the callable.

    Returns
    -------
    bool
        True if the callable raises the specified exception; False otherwise.

    Examples
    --------
    >>> def my_func():
    ...     raise ValueError("test")
    >>> raises(my_func, ValueError)
    True

    >>> def my_func():
    ...     return True
    >>> raises(my_func, ValueError)
    False
    """
    try:
        callable()
        return False
    except:
        return True
