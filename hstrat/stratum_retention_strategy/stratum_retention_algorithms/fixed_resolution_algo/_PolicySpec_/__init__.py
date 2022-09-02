from distutils.errors import CompileError

from ._PolicySpec import PolicySpec

impls = [
    PolicySpec,
]

try:
    import cppimport.import_hook

    from ._PolicySpecNative import PolicySpecNative
    impls.append(PolicySpecNative)
except (CompileError, ImportError, SystemExit):
    import os
    os.environ["HSTRAT_NATIVE_ERROR"] = "1"
    pass
