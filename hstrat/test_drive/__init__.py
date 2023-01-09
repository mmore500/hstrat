"""Tools to create phylogenies and corresponding extant populations of
hereditary stratigraph columns."""

from . import generate_template_phylogeny, perfect_tracking
from ._descend_template_phylogeny import descend_template_phylogeny
from ._descend_template_phylogeny_naive import descend_template_phylogeny_naive
from ._descend_template_phylogeny_posthoc import (
    descend_template_phylogeny_posthoc,
)
from .generate_template_phylogeny import *  # noqa: F401
from .perfect_tracking import *  # noqa: F401

# adapted from https://stackoverflow.com/a/31079085
__all__ = (
    [
        "descend_template_phylogeny",
        "descend_template_phylogeny_naive",
        "descend_template_phylogeny_posthoc",
    ]
    + generate_template_phylogeny.__all__
    + perfect_tracking.__all__
)

from .._auxiliary_lib import launder_impl_modules as _launder

_launder(
    [
        descend_template_phylogeny,
        descend_template_phylogeny_naive,
        descend_template_phylogeny_posthoc,
    ],
    __name__,
)
del _launder  # prevent name from leaking
