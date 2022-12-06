"""Top-level package for hstrat."""

__author__ = """Matthew Andres Moreno"""
__email__ = "m.more500@gmail.com"
__version__ = "1.0.5"

from . import (
    _auxiliary_lib,
    genome_instrumentation,
    juxtaposition,
    phylogenetic_inference,
    serialization,
    stratum_retention_strategy,
    stratum_retention_viz,
)

__all__ = [
    "_auxiliary_lib",
    "genome_instrumentation",
    "juxtaposition",
    "phylogenetic_inference",
    "serialization",
    "stratum_retention_strategy",
    "stratum_retention_viz",
]
