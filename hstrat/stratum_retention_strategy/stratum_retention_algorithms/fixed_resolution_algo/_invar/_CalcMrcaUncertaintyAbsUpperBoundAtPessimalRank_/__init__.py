import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank import (
    CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank,
)

impls = [
    CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank,
]

CalcMrcaUncertaintyAbsUpperBoundAtPessimalRankNative = opyt.apply_if(
    hstrat_import_native(
        "._CalcMrcaUncertaintyAbsUpperBoundAtPessimalRankNative", __name__
    ),
    lambda x: x.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRankNative,
)
if CalcMrcaUncertaintyAbsUpperBoundAtPessimalRankNative is not None:
    impls.append(CalcMrcaUncertaintyAbsUpperBoundAtPessimalRankNative)
