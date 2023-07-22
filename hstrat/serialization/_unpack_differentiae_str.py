from base64 import b64decode
import typing

from bitstring import BitArray
import numpy as np

from ._unpack_differentiae_bytes import unpack_differentiae_bytes


def unpack_differentiae_str(
    packed_differentiae: str,
    differentia_bit_width: int,
) -> typing.Iterator[int]:
    """Unpack a compact, concatenated base 64 representation into
    a sequence with each element represented as a distinct integer."""
    bytes_ = b64decode(packed_differentiae)
    yield from unpack_differentiae_bytes(bytes_, differentia_bit_width)
