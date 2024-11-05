"""Visualizations for stratum retention policies."""

from . import animate, ascii, plot
from .._auxiliary_lib import lazy_attach

__getattr__, __dir__, __all__ = lazy_attach(
    __name__,
    submodules=["animate", "ascii", "plot"],
    submod_attrs={
        "animate": animate.__all__,
        "ascii": ascii.__all__,
        "plot": plot.__all__,
    },
    should_launder=[].__contains__,
)
del lazy_attach
