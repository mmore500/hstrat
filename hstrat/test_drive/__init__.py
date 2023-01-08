"""Tools to create phylogenies and corresponding extant populations of
hereditary stratigraph columns."""

from ._descend_template_phylogeny import descend_template_phylogeny
from ._descend_template_phylogeny_naive import descend_template_phylogeny_naive
from ._descend_template_phylogeny_posthoc import (
    descend_template_phylogeny_posthoc,
)

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "descend_template_phylogeny",
    "descend_template_phylogeny_naive",
    "descend_template_phylogeny_posthoc",
]

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
