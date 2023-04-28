import opytional as opyt

from ...._auxiliary_lib import hstrat_import_native
from ._HereditaryStratumOrderedStoreDict import (
    HereditaryStratumOrderedStoreDict,
)

impls = [
    HereditaryStratumOrderedStoreDict,
]

# HereditaryStratumOrderedStoreDictNative = opyt.apply_if(
#     hstrat_import_native("._HereditaryStratumOrderedStoreDictNative", __name__),
#     lambda x: x.HereditaryStratumOrderedStoreDictNative,
# )
# if HereditaryStratumOrderedStoreDictNative is not None:
#     impls.append(HereditaryStratumOrderedStoreDictNative)
