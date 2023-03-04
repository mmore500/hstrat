import functools
import typing

from iterpop import iterpop as ip
import pandas as pd

from ..._auxiliary_lib import (
    HereditaryStratigraphicArtifact,
    alifestd_make_empty,
)
from ...juxtaposition import calc_probability_differentia_collision_between
from ._build_tree_trie_ensemble import build_tree_trie_ensemble
from .trie_postprocess import (
    assign_trie_origin_times_expected_value,
    assign_trie_origin_times_naive,
    sample_ancestral_rollbacks,
)


def build_tree_trie(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    force_common_ancestry: bool = False,
    progress_wrap: typing.Callable = lambda x: x,
    seed: typing.Optional[int] = 1,
    bias_adjustment: typing.Union[str, object, None] = None,
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
    seed : int, default
        Controls tiebreaking decisions in the algorithm.

        Pass an int for reproducible output across multiple function calls. The
        default value, 1, ensures reproducible output. Pass None to use
        existing RNG context directly.
    bias_adjustment : "sample_ancestral_rollbacks" or prior, optional
        TODO

    Returns
    -------
    pd.DataFrame
        The reconstructed phylogenetic tree in alife standard format.
    """

    # for simplicity, return early for this special case
    if len(population) == 0:
        return alifestd_make_empty()

    p_differentia_collision = calc_probability_differentia_collision_between(
        population[0], population[0]
    )
    if bias_adjustment is None:
        trie_postprocessor = assign_trie_origin_times_naive
    elif (
        isinstance(bias_adjustment, str)
        and bias_adjustment == "sample_ancestral_rollbacks"
    ):

        def trie_postprocessor(trie: TrieInnerNode) -> None:
            return assign_trie_origin_times_naive(
                sample_ancestral_rollbacks(
                    trie,
                    p_differentia_collision=p_differentia_collision,
                    seed=1,
                )
            )

    else:
        trie_postprocessor = functools.partial(
            assign_trie_origin_times_expected_value,
            prior=bias_adjustment,
        )

    return ip.popsingleton(
        build_tree_trie_ensemble(
            population=population,
            taxon_labels=taxon_labels,
            force_common_ancestry=force_common_ancestry,
            progress_wrap=progress_wrap,
            seed=seed,
            trie_postprocessors=[trie_postprocessor],
        )
    )
