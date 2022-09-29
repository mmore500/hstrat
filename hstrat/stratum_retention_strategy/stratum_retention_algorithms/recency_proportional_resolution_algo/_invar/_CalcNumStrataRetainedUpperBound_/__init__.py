import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._CalcNumStrataRetainedUpperBound import CalcNumStrataRetainedUpperBound

impls = [
    CalcNumStrataRetainedUpperBound,
]

# PolicySpecNative = opyt.apply_if(
# hstrat_import_native("._CalcNumStrataRetainedUpperBoundNative", __name__),
#     lambda x: x.CalcNumStrataRetainedUpperBoundNative,
# )
# if CalcNumStrataRetainedUpperBoundNative is not None:
#     impls.append(CalcNumStrataRetainedUpperBoundNative)
