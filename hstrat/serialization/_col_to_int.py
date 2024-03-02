import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._col_to_packet import col_to_packet
from ._impl import DEFAULT_PACKET_NUM_STRATA_DEPOSITED_BYTE_WIDTH


def col_to_int(
    column: HereditaryStratigraphicColumn,
    num_strata_deposited_byte_order: typing.Literal["big", "little"] = "big",
    num_strata_deposited_byte_width: int = (
        DEFAULT_PACKET_NUM_STRATA_DEPOSITED_BYTE_WIDTH
    ),
) -> int:
    """Serialize a `HereditaryStratigraphicColumn` to a binary representation
    as a Python int.

    Integer representation is packet binary representation plus a sentry bit at
    the most significant bit position, to prevent loss of leading zero bits.

    Uses big endian byte order.
    """

    if (
        not column._CanOmitStratumDepositionRank()
        or column.HasAnyAnnotations()
    ):
        raise NotImplementedError()

    buffer = col_to_packet(
        column=column,
        num_strata_deposited_byte_order=num_strata_deposited_byte_order,
        num_strata_deposited_byte_width=num_strata_deposited_byte_width,
    )
    buffer_num_bits = len(buffer) * 8
    sentry_bit = 1 << buffer_num_bits
    assert sentry_bit.bit_length() % 8 == 1
    semantic_value = int.from_bytes(buffer, byteorder="big", signed=False)
    assert semantic_value.bit_length() <= buffer_num_bits
    assert semantic_value & sentry_bit == 0

    return semantic_value | sentry_bit
