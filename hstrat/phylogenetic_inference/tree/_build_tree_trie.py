import contextlib
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
    RngStateContext,
    alifestd_collapse_unifurcations,
    alifestd_find_chronological_inconsistency,
    alifestd_is_chronologically_ordered,
    alifestd_make_empty,
    argsort,
    give_len,
)
from ...juxtaposition import (
    calc_probability_differentia_collision_between,
    calc_rank_of_first_retained_disparity_between,
    calc_rank_of_last_retained_commonality_between,
)
from ...stratum_retention_viz import col_to_ascii
from ..pairwise import (
    estimate_patristic_distance_between,
    estimate_rank_of_mrca_between,
    estimate_ranks_since_mrca_with,
)
from ..population import build_distance_matrix_biopython
from ..priors import ArbitraryPrior, UniformPrior
from ._impl import (
    TrieInnerNode,
    assign_trie_origin_times_naive,
    assign_trie_origin_times_unbiased,
    unzip_trie_expected_collisions,
)


def _build_tree_trie(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    estimator: str,
    prior: typing.Union[str, object],
    taxon_labels: typing.Optional[typing.Iterable],
    force_common_ancestry: bool,
    progress_wrap: typing.Callable,
) -> pd.DataFrame:
    """Implementation detail for build_tree_trie.

    See `build_tree_trie` for parameter descriptions.
    """

    # for simplicity, return early for this special case
    if len(population) == 0:
        return alifestd_make_empty()

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
            res = root.GetDeepestConsecutiveSharedAlleleGenesis(
                artifact.IterRankDifferentiaZip(copyable=True)
            )
            node, subsequent_allele_genesis_iter = res
            node.InsertTaxon(label, subsequent_allele_genesis_iter)

    # assign origin times
    if estimator == "maximum_likelihood" and prior == "arbitrary":
        assign_trie_origin_times_naive(root)
    elif estimator == "maximum_likelihood":
        raise NotImplementedError(estimator, prior)
    else:
        # setup prior
        if isinstance(prior, str):
            prior = {
                "arbitrary": ArbitraryPrior,
                "uniform": UniformPrior,
            }[prior]()

        {"unbiased": assign_trie_origin_times_unbiased,}[estimator](
            root,
            calc_probability_differentia_collision_between(*population[0:2]),
            prior,
        )

    # unzip expected differentia collisions
    if estimator == "unbiased":
        unzip_trie_expected_collisions(
            root,
            calc_probability_differentia_collision_between(*population[0:2]),
        )

    if not force_common_ancestry:
        try:
            root = ip.popsingleton(root.children)
            root.parent = None
        except:
            raise ValueError

    res = apc.anytree_tree_to_alife_dataframe(root)

    return alifestd_collapse_unifurcations(res, mutate=True)


def build_tree_trie(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    estimator: str,
    prior: typing.Union[str, object],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    force_common_ancestry: bool = False,
    progress_wrap: typing.Callable = lambda x: x,
    seed: typing.Optional[int] = 1,
) -> pd.DataFrame:
    """Estimate the phylogenetic history among hereditary stratigraphic
    columns using an agglomerative approach followed by progressive refinement.

    Parameters
    ----------
    population: Sequence[HereditaryStratigraphicArtifact]
        Hereditary stratigraphic columns corresponding to extant population members.

        Each member of population will correspond to a unique leaf node in the
        reconstructed tree.
    taxon_labels: Optional[Iterable], optional
        How should leaf nodes representing extant hereditary stratigraphic
        columns be named?

        Label order should correspond to the order of corresponding hereditary
        stratigraphic columns within `population`. If None, taxons will be
        named according to their numerical index.
    force_common_ancestry: bool, default False
        How should columns that definively share no common ancestry be handled?

        If set to True, treat columns with no common ancestry as if they
        shared a common ancestor immediately before the genesis of the
        lineages. If set to False, columns within `population` that
        definitively do not share common ancestry will raise a ValueError.
    progress_wrap : Callable, default identity function
        Wrapper applied around generation iterator and row generator for final
        phylogeny compilation process.

        Pass tqdm or equivalent to display progress bars.
    seed: int, default
        Controls tiebreaking decisions in the algorithm.

        Pass an int for reproducible output across multiple function calls. The default value, 1, ensures reproducible output. Pass
    Returns
    -------
    pd.DataFrame
        The reconstructed phylogenetic tree in alife standard format.
    """
    with opyt.apply_if_or_value(
        seed,
        RngStateContext,
        contextlib.nullcontext,
    ):
        return _build_tree_trie(
            population=population,
            estimator=estimator,
            prior=prior,
            taxon_labels=taxon_labels,
            force_common_ancestry=force_common_ancestry,
            progress_wrap=progress_wrap,
        )
