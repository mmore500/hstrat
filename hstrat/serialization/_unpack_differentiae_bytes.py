import itertools as it
import typing

from bitstring import BitArray
import numpy as np
import opytional as opyt
import typing_extensions

from .._auxiliary_lib import bytes_swap_bit_order, iter_chunks


def _numpy_unpack_differentiae(
    buffer: bytes, differentia_bit_width: int
) -> typing.Iterator[int]:
    # numpy dtypes can be composed of various attributes
    # in this case, we want our type to be big-endian (>),
    # and to be composed of `num_bytes` unsigned ints (u).
    # for more info, see https://numpy.org/doc/stable/reference/generated/numpy.dtype.html
    num_bytes = differentia_bit_width // 8
    dt = np.dtype(f">u{num_bytes}")
    yield from np.frombuffer(buffer, dtype=dt)


def _bitarray_unpack_differentiae(
    buffer: bytes,
    differentia_bit_width: int,
    differentiae_byte_bit_order: typing.Literal["big", "little"],
    num_packed_differentia: typing.Optional[int],
) -> typing.Iterator[int]:
    bits = BitArray(bytes=buffer)
    num_header_bits = (
        8
        if num_packed_differentia is None and bool(differentia_bit_width % 8)
        else 0
    )

    if num_packed_differentia is None:
        if len(bits) and num_header_bits:
            # undo to prevent num padding bits from being flipped by bit order
            r = {"big": 1, "little": -1}[differentiae_byte_bit_order]
            num_padding_bits = bits[:num_header_bits][::r].uint
        else:
            num_padding_bits = 0
        num_valid_bits = len(bits) - num_header_bits - num_padding_bits
        assert num_valid_bits % differentia_bit_width == 0
        num_packed_differentia = num_valid_bits // differentia_bit_width

    valid_bits = bits[num_header_bits:]
    assert (
        len([*iter_chunks(valid_bits, differentia_bit_width)])
        >= num_packed_differentia
    )
    for chunk in it.islice(
        iter_chunks(valid_bits, differentia_bit_width), num_packed_differentia
    ):
        yield chunk.uint


def unpack_differentiae_bytes(
    packed_differentiae: typing_extensions.Buffer,
    differentia_bit_width: int,
    differentiae_byte_bit_order: typing.Literal["big", "little"] = "big",
    num_packed_differentia: typing.Optional[int] = None,
) -> typing.Iterator[int]:
    """Unpack a compact, concatenated byte buffer representation into
    a sequence with each element represented as a distinct integer."""
    if opyt.or_value(num_packed_differentia, 0) < 0:
        raise ValueError

    if differentiae_byte_bit_order == "little":
        packed_differentiae = bytes_swap_bit_order(packed_differentiae)

    if differentia_bit_width in [8, 16, 32, 64]:
        # bit width is a multiple of 8 -- no padding required
        assert (
            num_packed_differentia is None
            or num_packed_differentia * differentia_bit_width
            == len(packed_differentiae) * 8
        )
        yield from _numpy_unpack_differentiae(
            packed_differentiae, differentia_bit_width
        )
    else:
        # padding bits are possible, first byte tells how many are required
        yield from _bitarray_unpack_differentiae(
            packed_differentiae,
            differentia_bit_width,
            differentiae_byte_bit_order,
            num_packed_differentia,
        )
