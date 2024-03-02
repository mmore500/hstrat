import typing

import typing_extensions

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._impl import DEFAULT_PACKET_NUM_STRATA_DEPOSITED_BYTE_WIDTH
from ._pack_differentiae_bytes import pack_differentiae_bytes


def col_to_packet(
    column: HereditaryStratigraphicColumn,
    num_strata_deposited_byte_order: typing.Literal["big", "little"] = "big",
    num_strata_deposited_byte_width: int = (
        DEFAULT_PACKET_NUM_STRATA_DEPOSITED_BYTE_WIDTH
    ),
) -> typing_extensions.Buffer:
    """Serialize a `HereditaryStratigraphicColumn` to a binary buffer."""

    if (
        not column._CanOmitStratumDepositionRank()
        or column.HasAnyAnnotations()
    ):
        raise NotImplementedError()

    total_differentia_bits = (
        column.GetNumStrataRetained() * column.GetStratumDifferentiaBitWidth()
    )
    total_differentia_bytes = (total_differentia_bits + 7) // 8  # +7 rounds up
    needs_num_padding_bits_header: bool = (
        bool(column.GetStratumDifferentiaBitWidth() % 8)
        and column._stratum_retention_policy.CalcNumStrataRetainedExact is None
    )
    if needs_num_padding_bits_header:
        # extra byte to encode num padding bits
        total_differentia_bytes += 1

    total_packet_bytes = (
        num_strata_deposited_byte_width + total_differentia_bytes
    )

    packet_buffer = bytearray(total_packet_bytes)
    assert len(packet_buffer) == total_packet_bytes
    packet_buffer[
        :num_strata_deposited_byte_width
    ] = column.GetNumStrataDeposited().to_bytes(
        num_strata_deposited_byte_width,
        byteorder=num_strata_deposited_byte_order,
        signed=False,
    )
    assert len(packet_buffer) == total_packet_bytes
    differentia_bytes = pack_differentiae_bytes(
        column.IterRetainedStrata(),
        column.GetStratumDifferentiaBitWidth(),
        always_omit_num_padding_bits_header=not needs_num_padding_bits_header,
    )
    assert len(differentia_bytes) == total_differentia_bytes, len(
        differentia_bytes
    )
    assert len(packet_buffer[num_strata_deposited_byte_width:]) == len(
        differentia_bytes
    )
    packet_buffer[num_strata_deposited_byte_width:] = differentia_bytes
    assert len(packet_buffer) == total_packet_bytes
    return packet_buffer
