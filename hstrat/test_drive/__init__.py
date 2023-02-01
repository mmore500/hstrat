"""Tools to create phylogenies and corresponding extant populations of
hereditary stratigraph columns."""

from . import (
    descend_template_phylogeny,
    generate_template_phylogeny,
    perfect_tracking,
)

# adapted from https://stackoverflow.com/a/31079085
__all__ = (
    descend_template_phylogeny.__all__
    + generate_template_phylogeny.__all__
    + perfect_tracking.__all__
)

from .descend_template_phylogeny import *  # noqa: F401
from .generate_template_phylogeny import *  # noqa: F401
from .perfect_tracking import *  # noqa: F401
