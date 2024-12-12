import importlib
import logging
import os
import types

import opytional as opyt

from ._except_wrap_sentinel import except_wrap_sentinel
from ._is_in_unit_test import is_in_unit_test


def _import_cppimport(module_name: str, package: str) -> types.ModuleType:
    """Implementation detail for load_cppimportable_module"""
    import cppimport

    return cppimport.imp(f"{package}.{module_name}")


def _import_importlib(module_name: str, package: str) -> types.ModuleType:
    """Implementation detail for load_cppimportable_module"""
    return importlib.import_module(f".{module_name}", package=package)


def load_cppimportable_module(
    module_name: str, package: str
) -> types.ModuleType:
    r"""Imports module, prioritizing cppimport if in unit test or requested
    by environment variable HSTRAT_USE_CPPIMPORT; otherwise, pre-existing
    precompiled binaries are prioritized.

    Parameters
    ----------
    module_name : str
        The name of the C++ module to import from.
    package : str
        The package where the C++ module is contained.

        Assuming this function is called in the same package as that, it should
        be something like `re.sub(r"\.[a-za-z0-9_]+$", '', __name__)`.

    Returns
    -------
    types.ModuleType
        The imported module.
    """

    def do_import_importlib() -> types.ModuleType:
        return _import_importlib(module_name, package)

    def do_import_cppimport() -> types.ModuleType:
        return _import_cppimport(module_name, package)

    in_unit_test = is_in_unit_test()
    if "HSTRAT_USE_CPPIMPORT" in os.environ or in_unit_test:
        if in_unit_test:
            logging.info(
                "unit test session detected, preferring cppimport over precompiled binaries",
            )
        primary, fallback = (
            except_wrap_sentinel(
                do_import_cppimport,
                {
                    ImportError: f"cppimport failed, falling back to precompiled binaries for '{package}.{module_name}'",
                    ModuleNotFoundError: f"cppimport not installed, falling back to native binaries for '{package}.{module_name}'",
                },
                sentinel=None,
            ),
            do_import_importlib,
        )
    else:
        primary, fallback = (
            except_wrap_sentinel(
                do_import_importlib,
                {
                    ImportError: f"precompiled binaries for '{package}.{module_name}' not found, falling back to cppimport",
                },
            ),
            do_import_cppimport,
        )

    return opyt.or_else(primary(), fallback)
