"""Convenient library repack as a flat namespace."""

from .._auxiliary_lib import get_hstrat_version
from ..frozen_instrumentation import *  # noqa: F401
from ..genome_instrumentation import *  # noqa: F401
from ..juxtaposition import *  # noqa: F401
from ..phylogenetic_inference import *  # noqa: F401
from ..serialization import *  # noqa: F401
from ..stratum_retention_strategy import *  # noqa: F401
from ..stratum_retention_viz import *  # noqa: F401
from ..test_drive import *  # noqa: F401

__version__ = get_hstrat_version()
