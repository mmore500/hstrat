from distutils.errors import CompileError
import importlib
import os
import types
import typing


def hstrat_import_native(
    name: str,
    package: str,
) -> typing.Optional[types.ModuleType]:
    """Attempt importing a native hstrat module.

    If the environment variable HSTRAT_CPPIMPORT_OPT_IN is not set,
    (potentially slow) module compilation will not be attempted. Use of native
    extensions will therefore require pre-existence of binaries.

    If the environment variable HSTRAT_RERAISE_IMPORT_NATIVE_EXCEPTION is not
    set, a failed compilation or import will result in a return value of None.
    If it is set, any exceptions will be reaised prevent silent import failure.

    The arguments 'name' and 'package are forwarded to importlib.import_module.
    The name argument specifies what module to import in absolute or relative
    terms (e.g. either pkg.mod or ..mod). If the name is specified in relative
    terms, then the package argument must be set to the name of the package
    which is to act as the anchor for resolving the package name (e.g.
    import_module('..mod', 'pkg.subpkg') will import pkg.mod).
    """

    try:
        if os.environ.get("HSTRAT_CPPIMPORT_OPT_IN", False):
            import cppimport.import_hook

        return importlib.import_module(name, package)
    except (CompileError, ImportError, SystemExit) as e:
        if os.environ.get("HSTRAT_RERAISE_IMPORT_NATIVE_EXCEPTION", False):
            raise e
        else:
            return None
