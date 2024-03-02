import typing

import typing_extensions

from .._auxiliary_lib import get_hstrat_version
from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._col_from_records import col_from_records
from ._impl import (
    DEFAULT_PACKET_NUM_STRATA_DEPOSITED_BYTE_WIDTH,
    stringify_packed_differentia_bytes,
)
from ._policy_to_records import policy_to_records


def col_from_packet(
    packet: typing_extensions.Buffer,
    differentia_bit_width: int,
    stratum_retention_policy: typing.Callable,
    differentiae_byte_bit_order: typing.Literal["big", "little"] = "big",
    num_strata_deposited_byte_order: typing.Literal["big", "little"] = "big",
    num_strata_deposited_byte_width: int = (
        DEFAULT_PACKET_NUM_STRATA_DEPOSITED_BYTE_WIDTH
    ),
) -> HereditaryStratigraphicColumn:
    """Deserialize a `HereditaryStratigraphicColumn` from a differentia packet
    and column configuration specification information.

    Use when buffer size equals packet size.

    See Also
    --------
    col_from_packet_buffer: use when buffer size exceeds packet size.
    """

    policy_records = policy_to_records(stratum_retention_policy)
    num_strata_deposited = int.from_bytes(
        packet[:num_strata_deposited_byte_width],
        byteorder=num_strata_deposited_byte_order,
        signed=False,
    )
    differentiae_records = {
        "num_strata_deposited": num_strata_deposited,
        "differentiae": stringify_packed_differentia_bytes(
            packet[num_strata_deposited_byte_width:],
        ),
        "omits_num_padding_bits_header": True,
        "differentia_bit_width": differentia_bit_width,
        "hstrat_version": get_hstrat_version(),
    }

    return col_from_records(
        {**policy_records, **differentiae_records},
        differentiae_byte_bit_order=differentiae_byte_bit_order,
    )
