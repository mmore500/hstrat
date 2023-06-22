import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._IterRetainedRanks import IterRetainedRanks

impls = [
    IterRetainedRanks,
]

# PolicySpecNative = opyt.apply_if(
# hstrat_import_native("._IterRetainedRanksNative", __name__),
#     lambda x: x.IterRetainedRanksNative,
# )
# if IterRetainedRanksNative is not None:
#     impls.append(IterRetainedRanksNative)
