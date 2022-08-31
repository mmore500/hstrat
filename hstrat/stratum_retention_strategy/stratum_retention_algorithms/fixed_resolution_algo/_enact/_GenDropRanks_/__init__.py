import cppimport.import_hook

from ._FromPredKeepRank import FromPredKeepRank
from ._GenDropRanks import GenDropRanks
from ._GenDropRanksNative import GenDropRanksNative

impls = (FromPredKeepRank, GenDropRanks, GenDropRanksNative)
