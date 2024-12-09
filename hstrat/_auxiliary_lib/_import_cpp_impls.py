import importlib
import logging
import os
import types

import opytional as opyt

from ._except_wrap import except_wrap
from ._is_in_unit_test import is_in_unit_test


def _import_cppimport(module_name: str, package: str) -> types.ModuleType:
    """Implementation detail for import_cpp_impls"""
    import cppimport

    return cppimport.imp(f"{package}.{module_name}")


def _import_importlib(module_name: str, package: str) -> types.ModuleType:
    """Implementation detail for import_cpp_impls"""
    return importlib.import_module(f"{package}.{module_name}")


def import_cpp_impls(module_name: str, package: str) -> types.ModuleType:
    r"""Imports module, delegating to cppimport if in unit test or requested
    by environment variable HSTRAT_USE_CPPIMPORT.

    Parameters
    ---------
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
            logging.info("unit test session detected -- applying cppimport first")
        primary, fallback = (
            except_wrap(
                do_import_cppimport,
                {
                    ImportError: f"Import using cppimport for '{module_name}' in '{package}' failed, trying native binaries",
                    ModuleNotFoundError: f"cppimport for '{module_name}' in '{package}' not found, trying native binaries",
                },
            ),
            do_import_importlib,
        )
    else:
        primary, fallback = (
            except_wrap(
                do_import_importlib,
                {
                    ImportError: f"Native binaries for '{module_name}' in '{package}' not found, attempting to use cppimport",
                    AttributeError: f"Requested symbols for '{module_name}' in '{package}' not found, attempting to update with cppimport",
                },
            ),
            do_import_cppimport,
        )

    return opyt.or_else(primary(), fallback)
