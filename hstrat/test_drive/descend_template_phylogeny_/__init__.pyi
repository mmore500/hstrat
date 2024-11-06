from ._descend_template_phylogeny import descend_template_phylogeny
from ._descend_template_phylogeny_alifestd import (
    descend_template_phylogeny_alifestd,
)
from ._descend_template_phylogeny_biopython import (
    descend_template_phylogeny_biopython,
)
from ._descend_template_phylogeny_dendropy import (
    descend_template_phylogeny_dendropy,
)
from ._descend_template_phylogeny_naive import descend_template_phylogeny_naive
from ._descend_template_phylogeny_networkx import (
    descend_template_phylogeny_networkx,
)
from ._descend_template_phylogeny_posthoc import (
    descend_template_phylogeny_posthoc,
)

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "descend_template_phylogeny",
    "descend_template_phylogeny_alifestd",
    "descend_template_phylogeny_biopython",
    "descend_template_phylogeny_dendropy",
    "descend_template_phylogeny_naive",
    "descend_template_phylogeny_networkx",
    "descend_template_phylogeny_posthoc",
]
