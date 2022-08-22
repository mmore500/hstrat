"""Data structures to annotate genomes with."""

from . import stratum_ordered_stores
from ._HereditaryStratigraphicColumn import HereditaryStratigraphicColumn
from ._HereditaryStratigraphicColumnBundle import (
    HereditaryStratigraphicColumnBundle,
)
from ._HereditaryStratum import HereditaryStratum
from .stratum_ordered_stores import *  # noqa: F401

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "HereditaryStratigraphicColumn",
    "HereditaryStratigraphicColumnBundle",
    "HereditaryStratum",
] + stratum_ordered_stores.__all__

from .._auxiliary_lib import launder_impl_modules as _launder

_launder(
    [
        HereditaryStratigraphicColumn,
        HereditaryStratigraphicColumnBundle,
        HereditaryStratum,
    ],
    __name__,
)
del _launder  # prevent name from leaking
