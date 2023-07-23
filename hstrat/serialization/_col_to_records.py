import typing

from .._auxiliary_lib import get_hstrat_version
from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._pack_differentiae_str import pack_differentiae_str
from ._policy_to_records import policy_to_records


def col_to_records(column: HereditaryStratigraphicColumn) -> typing.Dict:
    """Serialize a `HereditaryStratigraphicColumn` to a dict composed of
    builtin types."""
    differentia_bit_width = column.GetStratumDifferentiaBitWidth()
    packed_differentiae = pack_differentiae_str(
        column.IterRetainedStrata(),
        differentia_bit_width,
    )

    policy_records = policy_to_records(column._stratum_retention_policy)
    res = {
        **policy_records,
        **{
            "num_strata_deposited": column.GetNumStrataDeposited(),
            "differentiae": packed_differentiae,
            "differentia_bit_width": differentia_bit_width,
            "hstrat_version": get_hstrat_version(),
        },
    }
    if not column._ShouldOmitStratumDepositionRank():
        res["stratum_deposition_ranks"] = [
            stratum.GetDepositionRank()
            for stratum in column.IterRetainedStrata()
        ]
        assert (
            len(res["stratum_deposition_ranks"])
            <= column.GetNumStrataDeposited()
        )

    if column.HasAnyAnnotations():
        res["stratum_annotations"] = [
            stratum.GetAnnotation() for stratum in column.IterRetainedStrata()
        ]

    return res
