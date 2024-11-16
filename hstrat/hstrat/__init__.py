"""Convenient library repack as a flat namespace."""

from .. import dataframe as _dataframe
from .. import frozen_instrumentation as _frozen_instrumentation
from .. import genome_instrumentation as _genome_instrumentation
from .. import juxtaposition as _juxtaposition
from .. import phylogenetic_inference as _phylogenetic_inference
from .. import serialization as _serialization
from .. import stratum_retention_strategy as _stratum_retention_strategy
from .. import stratum_retention_viz as _stratum_retention_viz
from .. import test_drive as _test_drive
from .._auxiliary_lib import get_hstrat_version as _get_hstrat_version

_top_level_modules = (
    _dataframe,
    _frozen_instrumentation,
    _genome_instrumentation,
    _juxtaposition,
    _phylogenetic_inference,
    _serialization,
    _stratum_retention_strategy,
    _stratum_retention_viz,
    _test_drive,
)

__version__ = _get_hstrat_version()

__all__ = tuple(
    _item for _module in _top_level_modules for _item in _module.__all__
)


def __dir__() -> list:
    """Returns the entire symbol list."""
    return __all__


def __getattr__(name: str) -> object:
    """Allows for equivalent behavior to having `from mod import *`
    in this file without the load-time cost of star imports.
    Previously, this file eagerly imported every symbol from the
    below packages. Now, the symbol is only imported if determined
    to be in said package.
    """
    for _module in _top_level_modules:
        if name in _module.__all__:
            return getattr(_module, name)
    raise AttributeError(f"Flat namespace 'hstrat' has no attribute '{name}'")
