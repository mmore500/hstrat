import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._CalcMrcaUncertaintyRelUpperBound import CalcMrcaUncertaintyRelUpperBound

impls = [
    CalcMrcaUncertaintyRelUpperBound,
]

# PolicySpecNative = opyt.apply_if(
# hstrat_import_native("._CalcMrcaUncertaintyRelUpperBoundNative", __name__),
#     lambda x: x.CalcMrcaUncertaintyRelUpperBoundNative,
# )
# if CalcMrcaUncertaintyRelUpperBoundNative is not None:
#     impls.append(CalcMrcaUncertaintyRelUpperBoundNative)
