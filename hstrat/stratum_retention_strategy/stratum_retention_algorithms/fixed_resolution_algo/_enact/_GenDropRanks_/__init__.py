import opytional as opyt

from ......_auxiliary_lib import hstrat_import_native
from ._FromPredKeepRank import FromPredKeepRank
from ._GenDropRanks import GenDropRanks

impls = [
    FromPredKeepRank,
    GenDropRanks,
]

GenDropRanksNative = opyt.apply_if(
    hstrat_import_native("._GenDropRanksNative", __name__),
    lambda x: x.GenDropRanksNative,
)
if GenDropRanksNative is not None:
    impls.append(GenDropRanksNative)
