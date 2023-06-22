import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._CalcRankAtColumnIndex import CalcRankAtColumnIndex

impls = [
    CalcRankAtColumnIndex,
]

CalcRankAtColumnIndexNative = opyt.apply_if(
    hstrat_import_native("._CalcRankAtColumnIndexNative", __name__),
    lambda x: x.CalcRankAtColumnIndexNative,
)
if CalcRankAtColumnIndexNative is not None:
    impls.append(CalcRankAtColumnIndexNative)
