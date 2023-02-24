import typing


# adapted from https://stackoverflow.com/a/434328
def iter_chunks(
    seq: typing.Sequence,
    chunk_size: int,
    start: int = 0,
) -> typing.Iterator[typing.Sequence]:
    """Yield successive chunks of size `chunk_size` from sequence `seq`.

    Parameters
    ----------
    seq : Sequence
        The sequence to be chunked.
    chunk_size : int
        The size of each chunk.

    Returns
    -------
    Iterator[Sequence]
        A generator object that yields chunks of `seq` of size `chunk_size`.

    Examples
    --------
    >>> seq = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> chunk_size = 3
    >>> for chunk in iter_chunks(seq, chunk_size):
    ...     print(chunk)
    [1, 2, 3]
    [4, 5, 6]
    [7, 8, 9]
    [10]
    """
    return (
        seq[pos : pos + chunk_size]
        for pos in range(start, len(seq), chunk_size)
    )
