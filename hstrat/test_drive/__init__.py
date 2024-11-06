"""Tools to create phylogenies and corresponding extant populations of
hereditary stratigraph columns."""

from . import (
    descend_template_phylogeny_,
    generate_template_phylogeny,
    perfect_tracking,
)
from .._auxiliary_lib import lazy_attach

__getattr__, __dir__, __all__ = lazy_attach(
    __name__,
    submodules=[
        "descend_template_phylogeny_",
        "generate_template_phylogeny",
        "perfect_tracking",
    ],
    submod_attrs={
        "descend_template_phylogeny_": descend_template_phylogeny_.__all__,
        "generate_template_phylogeny": generate_template_phylogeny.__all__,
        "perfect_tracking": perfect_tracking.__all__,
    },
    should_launder=[].__contains__,
)
del lazy_attach
