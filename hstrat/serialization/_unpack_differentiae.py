import typing

from deprecated.sphinx import deprecated

from ._unpack_differentiae_str import unpack_differentiae_str


@deprecated(
    version="1.8.0",
    reason="Use unpack_differentiae_str instead.",
)
def unpack_differentiae(
    packed_differentiae: str,
    differentia_bit_width: int,
) -> typing.Iterator[int]:
    """Unpack a compact, concatenated base 64 representation into
    a sequence with each element represented as a distinct integer."""
    yield from unpack_differentiae_str(
        packed_differentiae, differentia_bit_width
    )
