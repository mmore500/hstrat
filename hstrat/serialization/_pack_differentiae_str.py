import typing

from ..genome_instrumentation import HereditaryStratum
from ._impl import stringify_packed_differentia_bytes
from ._pack_differentiae_bytes import pack_differentiae_bytes


def pack_differentiae_str(
    strata: typing.Iterable[HereditaryStratum],
    differentia_bit_width: int,
) -> str:
    """Pack a sequence of differentiae together into a compact string
    representation.

    Returns a string with base 64 encoded concatenation of diffferentiae.
    If `differentia_bit_width` is not an even byte multiple, the first encoded
    byte tells how many empty padding bits, if any, were placed at the end of
    the concatenation in order to align the bitstring end to byte boundaries.
    """

    buffer = pack_differentiae_bytes(strata, differentia_bit_width)
    return stringify_packed_differentia_bytes(buffer)
