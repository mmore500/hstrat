import typing

import Bio.Phylo.TreeConstruction as BioPhyloTree
import pandas as pd

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._impl import build_tree_biopython_distance


def build_tree_biopython_nj(
    population: typing.Sequence[HereditaryStratigraphicColumn],
    estimator: str,
    prior: typing.Union[str, typing.Any],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    force_common_ancestry: bool = False,
    return_as: str = "alifestd",
) -> typing.Union[pd.DataFrame, BioPhyloTree.BaseTree.Tree]:

    return build_tree_biopython_distance(
        "nj",
        population,
        estimator,
        prior,
        taxon_labels,
        force_common_ancestry,
        return_as,
    )
