import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._CalcMrcaUncertaintyRelExact import CalcMrcaUncertaintyRelExact

impls = [
    CalcMrcaUncertaintyRelExact,
]

# PolicySpecNative = opyt.apply_if(
# hstrat_import_native("._CalcMrcaUncertaintyRelExactNative", __name__),
#     lambda x: x.CalcMrcaUncertaintyRelExactNative,
# )
# if CalcMrcaUncertaintyRelExactNative is not None:
#     impls.append(CalcMrcaUncertaintyRelExactNative)
