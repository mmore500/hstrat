import typing

from .._auxiliary_lib import get_hstrat_version
from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._pack_differentiae import pack_differentiae


def col_to_records(column: HereditaryStratigraphicColumn) -> typing.Dict:
    """Serialize a `HereditaryStratigraphicColumn` to a dict composed of
    builtin types."""
    differentia_bit_width = column.GetStratumDifferentiaBitWidth()
    packed_differentiae = pack_differentiae(
        column.IterRetainedStrata(),
        differentia_bit_width,
    )

    policy = column._stratum_retention_policy
    spec = policy.GetSpec()
    res = {
        "policy_algo": spec.GetAlgoIdentifier(),
        "policy_spec": {
            k.lstrip("_"): v  # strip leading underscores on private members
            for k, v in spec.__dict__.items()
        },
        "policy": policy.GetEvalCtor(),
        "num_strata_deposited": column.GetNumStrataDeposited(),
        "differentiae": packed_differentiae,
        "differentia_bit_width": differentia_bit_width,
        "hstrat_version": get_hstrat_version(),
    }

    if not column._ShouldOmitStratumDepositionRank():
        res["stratum_deposition_ranks"] = [
            stratum.GetDepositionRank()
            for stratum in column.IterRetainedStrata()
        ]

    if column.HasAnyAnnotations():
        res["stratum_annotations"] = [
            stratum.GetAnnotation() for stratum in column.IterRetainedStrata()
        ]

    return res
