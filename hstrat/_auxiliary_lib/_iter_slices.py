import typing


# adapted from https://stackoverflow.com/a/434328
def iter_slices(
    len_seq: int,
    chunk_size: int,
    start: int = 0,
) -> typing.Iterator[slice]:
    """Returns an iterator of slices that chunk a sequence of length `len_seq`
    into `chunk_size` parts.

    Parameters
    ----------
    len_seq : int
        The length of the sequence to be chunked.
    chunk_size : int
        The size of each chunk in the sequence.
    start : int, optional
        The starting position of the first slice in the sequence. Defaults to 0.

    Returns
    -------
    typing.Iterator[slice]
        An iterator of slices representing the chunks of the sequence.

    Examples
    --------
    >>> list(iter_slices(10, 5))
    [slice(0, 5), slice(5, 10)]
    >>> list(iter_slices(10, 5, 2))
    [slice(2, 7), slice(7, 12)]
    >>> list(iter_slices(10, 10))
    [slice(0, 10)]
    """
    return (
        slice(pos, pos + chunk_size)
        for pos in range(start, len_seq, chunk_size)
    )
