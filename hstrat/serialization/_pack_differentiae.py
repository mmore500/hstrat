from base64 import b64encode
import typing

from bitarray import util as bitarray_util
from bitstring import BitArray

from .._auxiliary_lib import iter_slices, zip_strict
from ..genome_instrumentation import HereditaryStratum


def _make_buffer(strata, differentia_bit_width):
    try:
        len(strata)
    except TypeError:
        strata = [*strata]

    needs_header = bool(differentia_bit_width % 8)
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

    return buffer


def pack_differentiae(
    strata: typing.Iterable[HereditaryStratum],
    differentia_bit_width: int,
) -> str:
    """Pack a sequence of differentiae together into a compact
    representation.

    Returns a string with base 64 encoded concatenation of diffferentiae.
    If `differentia_bit_width` is not an even byte multiple, the first encoded
    byte tells how many empty padding bits, if any, were placed at the end of
    the concatenation in order to align the bitstring end to byte boundaries.
    """

    buffer = _make_buffer(strata, differentia_bit_width)

    encoded_bytes = b64encode(buffer.tobytes())

    encoded_str = encoded_bytes.decode()
    return encoded_str
