import importlib
import logging
import os
import typing

import opytional as opyt

from ._except_wrap import except_wrap


def _import_cppimport(
    module_name: str, package: str, requested_symbols: typing.List[str]
) -> typing.List[typing.Any]:
    import cppimport

    mod = cppimport.imp(f"{package}.{module_name}")
    return [getattr(mod, sym) for sym in requested_symbols]


def _import_normal(
    module_name: str, package: str, requested_symbols: typing.List[str]
) -> typing.List[typing.Any]:
    mod = importlib.import_module(f".{module_name}", package=package)
    return [getattr(mod, sym) for sym in requested_symbols]


def import_cpp_impls(
    module_name: str, package: str, requested_symbols: typing.List[str]
) -> typing.List[typing.Any]:
    r"""
    Returns symbols requested to be imported from

    Paramters
    ---------
    module_name : str
        The name of the C++ module to import from
    package : str
        The package where the C++ module is contained. Assuming this function
        is called in the same package as that, it should be something like
        `re.sub(r"\.[a-za-z0-9_]+$", '', __name__)`.
    requested_symbols : list[str]
        A list of symbols to import from the module.
    """

    normal_importer = lambda: _import_normal(
        module_name, package, requested_symbols
    )
    cppimport_importer = lambda: _import_cppimport(
        module_name, package, requested_symbols
    )

    using_pytest = "PYTEST_CURRENT_TEST" in os.environ
    if "HSTRAT_USE_CPPIMPORT" in os.environ or using_pytest:
        if using_pytest:
            logging.info("Pytest session detected -- applying cppimport")
        primary, fallback = except_wrap(
            cppimport_importer,
            {
                ImportError: "Import using cppimport failed, trying native binaries",
            },
        ), normal_importer
    else:
        primary, fallback = except_wrap(
            normal_importer,
            {
                ImportError: "Native binaries not found, attempting to use cppimport",
                AttributeError: "Requested symbols not found, attempting to update with cppimport",
            },
        ), cppimport_importer

    return opyt.or_else(primary(), fallback)
