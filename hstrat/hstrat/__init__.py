"""Convenient library repack as a flat namespace."""

from .. import frozen_instrumentation as __frozen_instrumentation
from .. import genome_instrumentation as __genome_instrumentation
from .. import juxtaposition as __juxtaposition
from .. import phylogenetic_inference as __phylogenetic_inference
from .. import serialization as __serialization
from .. import stratum_retention_strategy as __stratum_retention_strategy
from .. import stratum_retention_viz as __stratum_retention_viz
from .. import test_drive as __test_drive
from .._auxiliary_lib import get_hstrat_version
from ..frozen_instrumentation import __all__ as __frozen_instrumentation_all__
from ..genome_instrumentation import __all__ as __genome_instrumentation_all__
from ..juxtaposition import __all__ as __juxtaposition_all__
from ..phylogenetic_inference import __all__ as __phylogenetic_inference_all__
from ..serialization import __all__ as __serialization_all__
from ..stratum_retention_strategy import (
    __all__ as __stratum_retention_strategy_all__,
)
from ..stratum_retention_viz import __all__ as __stratum_retention_viz_all__
from ..test_drive import __all__ as __test_drive_all__

__version__ = get_hstrat_version()
del get_hstrat_version

__all__ = (
    __frozen_instrumentation_all__
    + __genome_instrumentation_all__
    + __juxtaposition_all__
    + __phylogenetic_inference_all__
    + __serialization_all__
    + __stratum_retention_strategy_all__
    + __stratum_retention_viz_all__
    + __test_drive_all__
)


def __dir__() -> list:
    """Returns the entire symbol list."""
    return __all__


def __getattr__(name: str) -> object:
    """Allows for equivalent behavior to having `from mod import *`
    in this file without the performance cost of star imports.
    Previously, this file eagerly imported every symbol from the
    below packages. Now, the symbol is only imported if determined
    to be in said package.
    """
    for mod, all__ in [
        (__frozen_instrumentation, __frozen_instrumentation_all__),
        (__genome_instrumentation, __genome_instrumentation_all__),
        (__juxtaposition, __juxtaposition_all__),
        (__phylogenetic_inference, __phylogenetic_inference_all__),
        (__serialization, __serialization_all__),
        (__stratum_retention_strategy, __stratum_retention_strategy_all__),
        (__stratum_retention_viz, __stratum_retention_viz_all__),
        (__test_drive, __test_drive_all__),
    ]:
        if name in all__:
            return getattr(mod, name)
    raise AttributeError(f"Flat namespace 'hstrat' has no attribute '{name}'")
