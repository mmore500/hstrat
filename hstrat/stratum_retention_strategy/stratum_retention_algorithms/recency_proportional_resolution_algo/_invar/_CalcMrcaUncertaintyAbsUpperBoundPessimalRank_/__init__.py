import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._CalcMrcaUncertaintyAbsUpperBoundPessimalRank import (
    CalcMrcaUncertaintyAbsUpperBoundPessimalRank,
)

impls = [
    CalcMrcaUncertaintyAbsUpperBoundPessimalRank,
]

# PolicySpecNative = opyt.apply_if(
# hstrat_import_native("._CalcMrcaUncertaintyAbsUpperBoundPessimalRankNative", __name__),
#     lambda x: x.CalcMrcaUncertaintyAbsUpperBoundPessimalRankNative,
# )
# if CalcMrcaUncertaintyAbsUpperBoundPessimalRankNative is not None:
#     impls.append(CalcMrcaUncertaintyAbsUpperBoundPessimalRankNative)
