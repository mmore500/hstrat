import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._CalcNumStrataRetainedExact import CalcNumStrataRetainedExact

impls = [
    CalcNumStrataRetainedExact,
]

# PolicySpecNative = opyt.apply_if(
# hstrat_import_native("._CalcNumStrataRetainedExactNative", __name__),
#     lambda x: x.CalcNumStrataRetainedExactNative,
# )
# if CalcNumStrataRetainedExactNative is not None:
#     impls.append(CalcNumStrataRetainedExactNative)
