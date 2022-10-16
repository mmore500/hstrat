import typing


# adapted from https://stackoverflow.com/a/434328
def iter_chunks(
    seq: typing.Sequence,
    chunk_size: int,
) -> typing.Iterator[typing.Sequence]:
    return (
        seq[pos : pos + chunk_size] for pos in range(0, len(seq), chunk_size)
    )
