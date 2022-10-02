import opytional as opyt

from ..._auxiliary_lib import hstrat_import_native
from ._HereditaryStratum import HereditaryStratum

impls = [
    HereditaryStratum,
]

# HereditaryStratumNative = opyt.apply_if(
#     hstrat_import_native("._HereditaryStratumNative", __name__),
#     lambda x: x.HereditaryStratumNative,
# )
# if HereditaryStratumNative is not None:
#     impls.append(HereditaryStratumNative)
