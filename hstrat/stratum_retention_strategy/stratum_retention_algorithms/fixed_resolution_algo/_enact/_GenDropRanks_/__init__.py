from distutils.errors import CompileError

from ._FromPredKeepRank import FromPredKeepRank
from ._GenDropRanks import GenDropRanks

impls = [
    FromPredKeepRank,
    GenDropRanks,
]

try:
    import cppimport.import_hook
    from ._GenDropRanksNative import GenDropRanksNative
    impls.append(GenDropRanksNative)
except (CompileError, ImportError, SystemExit):
    import os
    os.environ["HSTRAT_NATIVE_ERROR"] = "1"
    pass
