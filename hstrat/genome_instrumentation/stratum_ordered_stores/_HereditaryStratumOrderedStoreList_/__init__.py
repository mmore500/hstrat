import opytional as opyt

from ...._auxiliary_lib import hstrat_import_native
from ._HereditaryStratumOrderedStoreList import (
    HereditaryStratumOrderedStoreList,
)

impls = [
    HereditaryStratumOrderedStoreList,
]

# HereditaryStratumOrderedStoreListNative = opyt.apply_if(
#     hstrat_import_native("._HereditaryStratumOrderedStoreListNative", __name__),
#     lambda x: x.HereditaryStratumOrderedStoreListNative,
# )
# if HereditaryStratumOrderedStoreListNative is not None:
#     impls.append(HereditaryStratumOrderedStoreListNative)
