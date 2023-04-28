import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._CalcMrcaUncertaintyAbsExact import CalcMrcaUncertaintyAbsExact

impls = [
    CalcMrcaUncertaintyAbsExact,
]

CalcMrcaUncertaintyAbsExactNative = opyt.apply_if(
    hstrat_import_native("._CalcMrcaUncertaintyAbsExactNative", __name__),
    lambda x: x.CalcMrcaUncertaintyAbsExactNative,
)
if CalcMrcaUncertaintyAbsExactNative is not None:
    impls.append(CalcMrcaUncertaintyAbsExactNative)
