"""Convenient library repack as a flat namespace."""

from .._auxiliary_lib import get_hstrat_version

from .. import (
    frozen_instrumentation as __frozen_instrumentation,
    genome_instrumentation as __genome_instrumentation,
    juxtaposition as __juxtaposition,
    phylogenetic_inference as __phylogenetic_inference,
    serialization as __serialization,
    stratum_retention_strategy as __stratum_retention_strategy,
    stratum_retention_viz as __stratum_retention_viz,
    test_drive as __test_drive,
)


from ..frozen_instrumentation import __all__ as __frozen_instrumentation_all__
from ..genome_instrumentation import __all__ as __genome_instrumentation_all__
from ..juxtaposition import __all__ as __juxtaposition_all__
from ..phylogenetic_inference import __all__ as __phylogenetic_inference_all__
from ..serialization import __all__ as __serialization_all__
from ..stratum_retention_strategy import __all__ as __stratum_retention_strategy_all__
from ..stratum_retention_viz import __all__ as __stratum_retention_viz_all__
from ..test_drive import __all__ as __test_drive_all__


_DIR = [  # determined with from hstrat import hstrat; dir(hstrat)
    '__all__', '__builtins__', '__cached__',
    '__doc__', '__file__', '__getattr__',
    '__loader__', '__name__', '__package__',
    '__path__', '__spec__', '__version__',
]

__version__ = get_hstrat_version()
def __getattr__(name: str) -> None:
    if name in _DIR:
        return eval(name)  # potentially unsafe?
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
            return mod.__getattr__(name)
    raise AttributeError(f"Flat namespace 'hstrat' has no attribute '{name}'")
