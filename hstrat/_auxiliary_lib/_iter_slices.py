import typing


# adapted from https://stackoverflow.com/a/434328
def iter_slices(
    len_seq: int,
    chunk_size: int,
    start: int = 0,
) -> typing.Iterator[slice]:
    return (
        slice(pos, pos + chunk_size)
        for pos in range(start, len_seq, chunk_size)
    )
