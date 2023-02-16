import copy
import typing

import alifedata_phyloinformatics_convert as apc
import anytree
from iterpop import iterpop as ip
import opytional as opyt
import pandas as pd

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ...juxtaposition import (
    calc_rank_of_first_retained_disparity_between,
    calc_rank_of_last_retained_commonality_between,
)
from ..pairwise import (
    estimate_patristic_distance_between,
    estimate_rank_of_mrca_between,
    estimate_ranks_since_mrca_with,
)
from ..population import build_distance_matrix_biopython
from ._impl import GlomNode


def build_tree_glom(
    population: typing.Sequence[HereditaryStratigraphicColumn],
    # estimator: str,
    # prior: typing.Union[str, typing.Any],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    force_common_ancestry: bool = False,
) -> pd.DataFrame:
    """Estimate the phylogenetic history among hereditary stratigraphic
    columns using an agglomerative approach followed by progressive refinement.

    Parameters
    ----------
    population: Sequence[HereditaryStratigraphicColumn]
        Hereditary stratigraphic columns corresponding to extant population members.

        Each member of population will correspond to a unique leaf node in the
        reconstructed tree.
    estimator : {"maximum_likelihood", "unbiased"}
        What estimation method should be used? Options are "maximum_likelihood"
        or "unbiased".

        The "maximum_likelihood" estimator is faster to compute than the
        "unbiased" estimator. Unbiased estimator assumes a uniform prior for
        generation of MRCA.
    prior : {"arbitrary", "uniform"} or object implementing prior interface
        Prior probability density distribution over possible generations of the
        MRCA.

        Implementations for arbitrary, geometric, exponential, and uniform
        priors are available in hstrat.phylogenetic_inference.priors. User
        -defined classes specifying custom priors can also be provided.
    taxon_labels: Optional[Iterable], optional
        How should leaf nodes representing extant hereditary stratigraphic
        columns be named?

        Label order should correspond to the order of corresponding hereditary
        stratigraphic columns within `population`. If None, taxons will be
        named according to their numerical index.
    force_common_ancestry: bool, optional
        How should columns that definively share no common ancestry be handled?

        If set to True, treat columns with no common ancestry as if they
        shared a common ancestor immediately before the genesis of the
        lineages. If set to False, columns within `population` that
        definitively do not share common ancestry will raise a ValueError.

    Returns
    -------
    pd.DataFrame
        The reconstructed phylogenetic tree in alife standard format.
    """

    print()
    print(
        build_distance_matrix_biopython(
            population,
            "maximum_likelihood",
            "arbitrary",
            taxon_labels,
            force_common_ancestry or None,
        )
    )

    taxon_labels = opyt.or_value(
        taxon_labels,
        [*map(str, range(len(population)))],
    )
    taxon_label_lookup = {
        id(column): taxon_label
        for column, taxon_label in zip(population, taxon_labels)
    }

    glom_root = GlomNode(origin_time=0)

    for column in population:
        glom_root.PercolateColumn(column)
        print()
        for pre, __, node in anytree.RenderTree(glom_root):
            print(f"{pre} {node.origin_time} {node.name}")

    print()
    print([*zip(taxon_labels, map(id, population))])

    internal_counter = 1
    for node in anytree.PreOrderIter(glom_root):
        if node.is_leaf:
            node.taxon_label = taxon_label_lookup[
                id(ip.popsingleton(node._leaves))
            ]
        else:
            node.taxon_label = f"Internal{internal_counter}"
            internal_counter += 1

    return apc.anytree_tree_to_alife_dataframe(glom_root)
