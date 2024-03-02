import itertools as it
import typing

from .._auxiliary_lib import get_hstrat_version, log_once_in_a_row
from ..genome_instrumentation import (
    HereditaryStratigraphicColumn,
    HereditaryStratumOrderedStoreList,
)
from ._impl import policy_from_record
from ._unpack_differentiae_str import unpack_differentiae_str


def col_from_records(
    records: typing.Dict,
    differentiae_byte_bit_order: typing.Literal["big", "little"] = "big",
) -> HereditaryStratigraphicColumn:
    """Deserialize a `HereditaryStratigraphicColumn` from a dict composed of
    builtin data types.
    """
    if get_hstrat_version() != records["hstrat_version"]:
        log_once_in_a_row(
            f"""col_from_records version mismatch, record is version {
                records['hstrat_version']
            } and software is version {
                get_hstrat_version()
            }"""
        )

    policy = policy_from_record(records["policy"])

    def load_stratum_ordered_store() -> HereditaryStratumOrderedStoreList:
        dummy_column = HereditaryStratigraphicColumn(
            stratum_retention_policy=policy_from_record(records["policy"]),
            stratum_differentia_bit_width=records["differentia_bit_width"],
            always_store_rank_in_stratum=(
                "stratum_deposition_ranks" in records
            ),
        )
        store = HereditaryStratumOrderedStoreList()

        for differentia, deposition_rank, annotation in zip(
            unpack_differentiae_str(
                records["differentiae"],
                differentia_bit_width=records["differentia_bit_width"],
                differentiae_byte_bit_order=differentiae_byte_bit_order,
                num_packed_differentia=(
                    None
                    if not records.get("omits_num_padding_bits_header", False)
                    else policy.CalcNumStrataRetainedExact(
                        records["num_strata_deposited"],
                    )
                ),
            ),
            records.get("stratum_deposition_ranks", it.repeat(None)),
            records.get("stratum_annotations", it.repeat(None)),
        ):
            store.DepositStratum(
                rank=deposition_rank,
                stratum=dummy_column._CreateStratum(
                    annotation=annotation,
                    differentia=differentia,
                    deposition_rank=deposition_rank,
                ),
            )

        if policy.CalcNumStrataRetainedExact is not None:
            assert (
                store.GetNumStrataRetained()
                == policy.CalcNumStrataRetainedExact(
                    records["num_strata_deposited"]
                )
            )

        return store

    return HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=records["differentia_bit_width"],
        stratum_ordered_store=(
            load_stratum_ordered_store(),
            records["num_strata_deposited"],
        ),
        always_store_rank_in_stratum=("stratum_deposition_ranks" in records),
    )
