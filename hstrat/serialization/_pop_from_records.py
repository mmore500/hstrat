import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._col_from_records import col_from_records


def pop_from_records(
    records: typing.Dict,
) -> typing.List[HereditaryStratigraphicColumn]:
    """Deserialize a sequence of `HereditaryStratigraphicColumn`s from a dict
    composed of builtin types."""

    col_records = records["columns"]
    for common_field in (
        "policy",
        "policy_algo",
        "policy_spec",
        "differentia_bit_width",
        "hstrat_version",
    ):
        for col_record in col_records:
            col_record[common_field] = records[common_field]

    return [col_from_records(col_record) for col_record in col_records]
