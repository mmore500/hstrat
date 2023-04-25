import random
import typing

from ._unzip import unzip


def coshuffled(*args) -> typing.Tuple:
    """Apply a consistent shuffle to multiple sequences.

    Parameters
    ----------
    *args : sequence of array-like objects
        Sequence of array-like objects that need to be shuffled together.

    Returns
    -------
    tuple
        A tuple with shuffled copies of `args` array-like objects.

    Notes
    -----
    This function shuffles multiple sequences of data together using the `zip` and `shuffle` functions from the built-in
    `random` module.

    Examples
    --------
    >>> x = [1, 2, 3]
    >>> y = [4, 5, 6]
    >>> z = [7, 8, 9]
    >>> coshuffled(x, y, z)
    ([2, 3, 1], [5, 6, 4], [8, 9, 7])
    """
    # if len(args) == 1:

    zipped = [*zip(*args)]
    random.shuffle(zipped)
    return tuple(map(list, unzip(zipped))) or tuple([] for __ in args)
