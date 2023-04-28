import opytional as opyt

from ...._auxiliary_lib import hstrat_import_native
from ._HereditaryStratumOrderedStoreTree import (
    HereditaryStratumOrderedStoreTree,
)

impls = [
    HereditaryStratumOrderedStoreTree,
]

# HereditaryStratumOrderedStoreTreeNative = opyt.apply_if(
#     hstrat_import_native("._HereditaryStratumOrderedStoreTreeNative", __name__),
#     lambda x: x.HereditaryStratumOrderedStoreTreeNative,
# )
# if HereditaryStratumOrderedStoreTreeNative is not None:
#     impls.append(HereditaryStratumOrderedStoreTreeNative)
