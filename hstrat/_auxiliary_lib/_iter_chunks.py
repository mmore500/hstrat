import typing


# adapted from https://stackoverflow.com/a/434328
def iter_chunks(
    seq: typing.Sequence,
    chunk_size: int,
    start: int = 0,
) -> typing.Iterator[typing.Sequence]:
    """Iterate over a sequence in chunks of a specified size.

    Parameters
    ----------
    seq : typing.Sequence
        Input sequence to be chunked.
    chunk_size : int
        The size of each chunk.
    start : int, optional
        Position of beginning of the first chunk (default 0).

    Returns
    -------
    typing.Iterator[typing.Sequence]
        Iterator that yields chunks of size `chunk_size` from `seq`.

    Examples
    --------
    >>> list(iter_chunks(range(10), chunk_size=2))
    [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
    >>> list(iter_chunks(range(10), chunk_size=3, start=2))
    [[2, 3, 4], [5, 6, 7], [8, 9]]
    """
    return (
        seq[pos : pos + chunk_size]
        for pos in range(start, len(seq), chunk_size)
    )
