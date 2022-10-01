import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._CalcMrcaUncertaintyRelUpperBoundAtPessimalRank import (
    CalcMrcaUncertaintyRelUpperBoundAtPessimalRank,
)

impls = [
    CalcMrcaUncertaintyRelUpperBoundAtPessimalRank,
]

CalcMrcaUncertaintyRelUpperBoundAtPessimalRankNative = opyt.apply_if(
    hstrat_import_native(
        "._CalcMrcaUncertaintyRelUpperBoundAtPessimalRankNative", __name__
    ),
    lambda x: x.CalcMrcaUncertaintyRelUpperBoundAtPessimalRankNative,
)
if CalcMrcaUncertaintyRelUpperBoundAtPessimalRankNative is not None:
    impls.append(CalcMrcaUncertaintyRelUpperBoundAtPessimalRankNative)
