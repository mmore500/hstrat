from base64 import b64decode
import typing
import numpy as np

from bitstring import BitArray

from .._auxiliary_lib import iter_chunks


def unpack_differentiae(
    packed_differentiae: str,
    differentia_bit_width: int,
) -> typing.Iterable[int]:
    """Unpack a compact, concatenated base 64 representation into
    a sequence of differentiae.
    """
    _bytes = b64decode(packed_differentiae)

    if differentia_bit_width in [8, 16, 32, 64]:
        # bit width is a multiple of 8 -- no padding required
        dt = np.dtype(f'>u{differentia_bit_width // 8}')
        yield from np.frombuffer(_bytes, dtype=dt)
    else:
        # padding bits are possible, first byte tells how many are required
        bits = BitArray(bytes=_bytes)
        num_padding_bits = bits[:8].uint
        if num_padding_bits:
            valid_bits = bits[8:-num_padding_bits]
        else:
            valid_bits = bits[8:]

        assert len(valid_bits) % differentia_bit_width == 0

        for chunk in iter_chunks(valid_bits, differentia_bit_width):
            yield chunk.uint
