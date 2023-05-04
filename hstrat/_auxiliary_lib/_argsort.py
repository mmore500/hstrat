import typing


# adapted from http://stackoverflow.com/questions/3071415/
def argsort(seq: typing.Sequence, reverse: bool = False) -> typing.List[int]:
    """Return the indices that would sort a sequence in ascending order.

    Parameters
    ----------
    seq : sequence
        Input sequence to be sorted.
    reverse : bool, optional
        If True, the indices that would sort the sequence in descending order
        are returned instead.
        Default is False.

    Returns
    -------
    indices : list of int
        List of indices that would sort the sequence.

    Notes
    -----
    This function is analogous to numpy.argsort.

    Examples
    --------
    >>> seq = [4.0, 2.0, 1.0, 3.0]
    >>> argsort(seq)
    [2, 1, 3, 0]
    >>> argsort(seq, reverse=True)
    [0, 3, 1, 2]
    """
    return sorted(range(len(seq)), key=seq.__getitem__, reverse=reverse)
