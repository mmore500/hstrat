import copy
import logging
import typing

import alifedata_phyloinformatics_convert as apc
import anytree
from iterpop import iterpop as ip
import opytional as opyt
import pandas as pd

from ..._auxiliary_lib import (
    HereditaryStratigraphicArtifact,
    alifestd_find_chronological_inconsistency,
    alifestd_is_chronologically_ordered,
    alifestd_make_empty,
    argsort,
    give_len,
)
from ...juxtaposition import (
    calc_rank_of_first_retained_disparity_between,
    calc_rank_of_last_retained_commonality_between,
)
from ...stratum_retention_viz import col_to_ascii
from ..pairwise import (
    estimate_patristic_distance_between,
    estimate_rank_of_mrca_between,
    estimate_ranks_since_mrca_with,
)
from ..population import (
    build_distance_matrix_biopython,
    does_definitively_share_no_common_ancestor,
)
from ._impl import TrieInnerNode


def build_tree_trie(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    # estimator: str,
    # prior: typing.Union[str, typing.Any],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    force_common_ancestry: bool = False,
    progress_wrap=lambda x: x,
) -> pd.DataFrame:
    """Estimate the phylogenetic history among hereditary stratigraphic
    columns using an agglomerative approach followed by progressive refinement.

    Parameters
    ----------
    population: Sequence[HereditaryStratigraphicArtifact]
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

    # for simplicity, return early for this special case
    if len(population) == 0:
        return alifestd_make_empty()

    if force_common_ancestry:
        raise NotImplementedError
    elif does_definitively_share_no_common_ancestor(population):
        raise ValueError

    taxon_labels = opyt.or_value(
        taxon_labels,
        [*map(str, range(len(population)))],
    )

    root = TrieInnerNode(rank=None, differentia=None)

    is_perfectly_synchronous = all(
        artifact.GetNumStrataDeposited()
        == population[0].GetNumStrataDeposited()
        for artifact in population
    )

    sort_order = argsort([x.GetNumStrataDeposited() for x in population])
    sorted_labels = [taxon_labels[i] for i in sort_order]
    sorted_population = [population[i] for i in sort_order]
    for label, artifact in progress_wrap(
        give_len(zip(sorted_labels, sorted_population), len(population))
    ):

        if is_perfectly_synchronous:
            root.InsertTaxon(label, artifact.IterRankDifferentiaZip())
        else:
            target = root.GetDeepestAlignment(
                artifact.IterRankDifferentiaZip(copyable=True)
            )
            if target is not None:
                target.InsertCachedTaxon(label)
            else:
                root.InsertTaxon(label, artifact.IterRankDifferentiaZip())

    res = apc.anytree_tree_to_alife_dataframe(root)

    return res
