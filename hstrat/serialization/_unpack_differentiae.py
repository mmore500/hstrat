from base64 import b64decode
import typing

from bitstring import BitArray

from .._auxiliary_lib import iter_chunks


def unpack_differentiae(
    packed_differentiae: str,
    differentia_bit_width: int,
) -> typing.Iterable[int]:

    _bytes = b64decode(packed_differentiae)
    bits = BitArray(bytes=_bytes)

    # if null bits are possible, first byte tells how many
    if differentia_bit_width % 8:
        num_null_bits = bits[:8].uint
        if num_null_bits:
            valid_bits = bits[8:-num_null_bits]
        else:
            valid_bits = bits[8:]
    else:
        valid_bits = bits[:]

    assert len(valid_bits) % differentia_bit_width == 0

    for chunk in iter_chunks(valid_bits, differentia_bit_width):
        yield chunk.uint
