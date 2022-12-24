from base64 import b64encode
import typing

from bitstring import BitArray

from ..genome_instrumentation import HereditaryStratum


def pack_differentiae(
    strata: typing.Iterable[HereditaryStratum],
    differentia_bit_width: int,
) -> str:

    # this is a concatenation, not a mathematical sum
    differentia_bits = sum(
        (
            BitArray(
                uint=stratum.GetDifferentia(),
                length=differentia_bit_width,
            )
            for stratum in strata
        ),
        BitArray(),
    )

    # use first byte to tell how many padding bits if any are required
    if differentia_bit_width % 8:
        num_jagged_bits = len(differentia_bits) % 8
        num_padding_bits = (8 - num_jagged_bits) % 8
        header = BitArray(
            uint=num_padding_bits,
            length=8,
        )
        differentia_bits = header + differentia_bits

    encoded_bytes = b64encode(differentia_bits.tobytes())

    encoded_str = encoded_bytes.decode()
    return encoded_str
