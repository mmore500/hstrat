from base64 import b64decode
import typing

from bitstring import BitArray
import numpy as np

from .._auxiliary_lib import iter_chunks


def _numpy_unpack_differentiae(
    _bytes: bytes, differentia_bit_width: int
) -> typing.Iterator[int]:
    # numpy dtypes can be composed of various attributes
    # in this case, we want our type to be big-endian (>),
    # and to be composed of `num_bytes` unsigned ints (u).
    # for more info, see https://numpy.org/doc/stable/reference/generated/numpy.dtype.html
    num_bytes = differentia_bit_width // 8
    dt = np.dtype(f">u{num_bytes}")
    yield from np.frombuffer(_bytes, dtype=dt)


def _bitarray_unpack_differentiae(
    _bytes: bytes, differentia_bit_width: int
) -> typing.Iterator[int]:
    bits = BitArray(bytes=_bytes)
    num_padding_bits = bits[:8].uint
    if num_padding_bits:
        valid_bits = bits[8:-num_padding_bits]
    else:
        valid_bits = bits[8:]

    assert len(valid_bits) % differentia_bit_width == 0

    for chunk in iter_chunks(valid_bits, differentia_bit_width):
        yield chunk.uint


def unpack_differentiae(
    packed_differentiae: str,
    differentia_bit_width: int,
) -> typing.Iterator[int]:
    """Unpack a compact, concatenated base 64 representation into
    a sequence with each element represented as a distinct integer."""
    _bytes = b64decode(packed_differentiae)

    if differentia_bit_width in [8, 16, 32, 64]:
        # bit width is a multiple of 8 -- no padding required
        yield from _numpy_unpack_differentiae(_bytes, differentia_bit_width)
    else:
        # padding bits are possible, first byte tells how many are required
        yield from _bitarray_unpack_differentiae(_bytes, differentia_bit_width)
