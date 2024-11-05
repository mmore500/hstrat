"""Data structures to annotate genomes with."""

from . import stratum_ordered_stores
from .._auxiliary_lib import lazy_attach

__getattr__, __dir__, __all__ = lazy_attach(
    __name__,
    submodules=["stratum_ordered_stores"],
    submod_attrs={
        "stratum_ordered_stores": stratum_ordered_stores.__all__,
        "_HereditaryStratigraphicColumn": ["HereditaryStratigraphicColumn"],
        "_HereditaryStratum": ["HereditaryStratum"],
        "_HereditaryStratigraphicColumnBundle": [
            "HereditaryStratigraphicColumnBundle",
        ],
    },
    should_launder=[
        "HereditaryStratigraphicColumn",
        "HereditaryStratum",
        "HereditaryStratigraphicColumnBundle",
    ].__contains__,
)
del lazy_attach
