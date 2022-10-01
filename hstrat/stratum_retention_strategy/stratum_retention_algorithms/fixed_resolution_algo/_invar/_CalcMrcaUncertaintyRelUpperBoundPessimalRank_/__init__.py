import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._CalcMrcaUncertaintyRelUpperBoundPessimalRank import (
    CalcMrcaUncertaintyRelUpperBoundPessimalRank,
)

impls = [
    CalcMrcaUncertaintyRelUpperBoundPessimalRank,
]

CalcMrcaUncertaintyRelUpperBoundPessimalRankNative = opyt.apply_if(
    hstrat_import_native(
        "._CalcMrcaUncertaintyRelUpperBoundPessimalRankNative", __name__
    ),
    lambda x: x.CalcMrcaUncertaintyRelUpperBoundPessimalRankNative,
)
if CalcMrcaUncertaintyRelUpperBoundPessimalRankNative is not None:
    impls.append(CalcMrcaUncertaintyRelUpperBoundPessimalRankNative)
