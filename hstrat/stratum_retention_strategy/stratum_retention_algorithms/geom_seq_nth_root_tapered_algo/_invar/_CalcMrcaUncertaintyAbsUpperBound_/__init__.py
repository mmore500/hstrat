import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._CalcMrcaUncertaintyAbsUpperBound import CalcMrcaUncertaintyAbsUpperBound

impls = [
    CalcMrcaUncertaintyAbsUpperBound,
]

# PolicySpecNative = opyt.apply_if(
# hstrat_import_native("._CalcMrcaUncertaintyAbsUpperBoundNative", __name__),
#     lambda x: x.CalcMrcaUncertaintyAbsUpperBoundNative,
# )
# if CalcMrcaUncertaintyAbsUpperBoundNative is not None:
#     impls.append(CalcMrcaUncertaintyAbsUpperBoundNative)
