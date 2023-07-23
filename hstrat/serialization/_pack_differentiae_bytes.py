import sys
import typing

from bitarray import util as bitarray_util
import numpy as np
import typing_extensions

from .._auxiliary_lib import iter_slices, zip_strict
from ..genome_instrumentation import HereditaryStratum


def _make_buffer_bitarray(
    strata: typing.Iterable[HereditaryStratum],
    differentia_bit_width: int,
    always_omit_num_padding_bits_header: bool,
) -> typing_extensions.Buffer:
    try:
        len(strata)
    except TypeError:
        strata = [*strata]

    needs_header = (
        bool(differentia_bit_width % 8)
        and not always_omit_num_padding_bits_header
    )
    buffer_size = 8 * needs_header + len(strata) * differentia_bit_width
    buffer = bitarray_util.zeros(buffer_size)

    # use first byte to tell how many padding bits if any are required
    if needs_header:
        num_jagged_bits = len(buffer) % 8
        num_padding_bits = (8 - num_jagged_bits) % 8
        header = bitarray_util.int2ba(
            num_padding_bits,
            length=8,
        )
        buffer[:8] |= header

    for slice_, stratum in zip_strict(
        iter_slices(len(buffer), differentia_bit_width, needs_header * 8),
        strata,
    ):
        buffer[slice_] |= bitarray_util.int2ba(
            stratum.GetDifferentia(), length=differentia_bit_width
        )

    return buffer.tobytes()


def _make_buffer_numpy(
    strata: typing.Iterable[HereditaryStratum],
    differentia_bit_width: int,
) -> typing_extensions.Buffer:
    buffer = np.fromiter(
        (s.GetDifferentia() for s in strata),
        dtype=eval(f"np.uint{differentia_bit_width}"),
    )
    if {
        ">": "big",
        "<": "little",
        "=": sys.byteorder,
        "|": "not applicable",
    }[buffer.dtype.byteorder] == "little":
        buffer.byteswap(inplace=True)
    return buffer.tobytes()


def pack_differentiae_bytes(
    strata: typing.Iterable[HereditaryStratum],
    differentia_bit_width: int,
    always_omit_num_padding_bits_header: bool = False,
) -> typing_extensions.Buffer:
    """Pack a sequence of differentiae together into a compact
    representation.

    Returns a byte buffer concatenation of diffferentiae. If
    `differentia_bit_width` is not an even byte multiple, the first encoded
    byte tells how many empty padding bits, if any, were placed at the end of
    the concatenation in order to align the bitstring end to byte boundaries.
    """
    strata = [*strata]
    if differentia_bit_width in (8, 16, 32, 64):
        return _make_buffer_numpy(strata, differentia_bit_width)
    else:
        return _make_buffer_bitarray(
            strata, differentia_bit_width, always_omit_num_padding_bits_header
        )
