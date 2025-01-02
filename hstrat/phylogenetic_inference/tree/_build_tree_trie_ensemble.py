import contextlib
import typing

import opytional as opyt
import pandas as pd

from ..._auxiliary_lib import (
    HereditaryStratigraphicArtifact,
    RngStateContext,
    alifestd_collapse_unifurcations,
    alifestd_make_empty,
    anytree_tree_to_alife_dataframe,
    flag_last,
)
from ...juxtaposition import calc_probability_differentia_collision_between
from ._impl import TrieInnerNode, build_trie_from_artifacts


def _finalize_trie(trie: TrieInnerNode) -> pd.DataFrame:
    "Convert to alifestd dataframe and collapse unifurcations."
    return alifestd_collapse_unifurcations(
        anytree_tree_to_alife_dataframe(trie), mutate=True
    )


def _build_tree_trie_ensemble(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    trie_postprocessors: typing.Iterable[typing.Callable],
    taxon_labels: typing.Optional[typing.Iterable],
    force_common_ancestry: bool,
    progress_wrap: typing.Callable,
) -> typing.List[pd.DataFrame]:
    """Implementation detail for build_tree_trie_ensemble.

    See `build_tree_trie_ensemble` for parameter descriptions.
    """
    # for simplicity, return early for this special case
    if len(population) == 0:
        res = alifestd_make_empty()
        res["origin_time"] = pd.Series(dtype=int)
        res["taxon_label"] = None
        return res

    root = build_trie_from_artifacts(
        population=population,
        taxon_labels=taxon_labels,
        progress_wrap=progress_wrap,
    )
    if not force_common_ancestry:
        try:
            (root,) = root.children
            root.parent = None
        except ValueError:
            raise ValueError(
                "Reconstruction resulted in multiple independent trees, "
                "due to artifacts definitively sharing no common ancestor. "
                "Consider setting force_common_ancestry=True.",
            )

    p_differentia_collision = calc_probability_differentia_collision_between(
        population[0], population[0]
    )

    res = []
    for is_last, postprocessor in flag_last(trie_postprocessors):
        res.append(
            _finalize_trie(
                postprocessor(
                    root,
                    p_differentia_collision=p_differentia_collision,
                    mutate=is_last,
                    progress_wrap=progress_wrap,
                ),
            ),
        )

    return res


def build_tree_trie_ensemble(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    trie_postprocessors: typing.Sequence[typing.Callable],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    force_common_ancestry: bool = False,
    progress_wrap: typing.Callable = lambda x: x,
    seed: typing.Optional[int] = 1,
) -> typing.List[pd.DataFrame]:
    """Estimate the phylogenetic history among hereditary stratigraphic
    columns by building a trie (a.k.a. prefix tree) of the differentia
    sequences of hereditary stratigraphic artifacts within a population.

    Returns phylogeny reconstruction outcomes from alternate postprocessing
    schemes applied between trie contruction and conversion to an alife
    standard data frame, including ancestor taxon origin time estimation.
    Because the underlying pre-postprocess trie is only constructed once, this
    method allows for efficient comparison of potprocessing schemes.

    Unless comparing alternate postprocessing schemes or applying a custom
    postprocessing option, end users should likely prefer `build_tree_trie`.
    This interface applies a single postprocess, set to a generally-appropriate
    default with a few other curated postprocesses specifiable by optional
    argument.

    Parameters
    ----------
    population: Sequence[HereditaryStratigraphicArtifact]
        Hereditary stratigraphic columns corresponding to extant population
        members.

        Each member of population will correspond to a unique leaf node in the
        reconstructed tree.
    trie_postprocessors: Iterable[Callable]
        Tree postprocess functors.

        Must take `trie` of type `TrieInnerNode`, `p_differentia_collision` of
        type `float`, `mutate` of type `bool`, and `progress_wrap` of type
        `Callable` params. Must returned postprocessed trie (type
        `TrieInnerNode`).

        Each postprocess will be called indpendently to produce a returned
        postprocessed variant. Use `CompoundTriePostprocessor` to chain
        postprocess functors that should be applied in succession.
    taxon_labels: Optional[Iterable], optional
        How should leaf nodes representing extant hereditary stratigraphic
        columns be named?

        Label order should correspond to the order of corresponding hereditary
        stratigraphic columns within `population`. If None, taxons will be
        named according to their numerical index.
    force_common_ancestry: bool, default False
        How should columns that definitively share no common ancestry be
        handled?

        If set to True, treat columns with no common ancestry as if they
        shared a common ancestor immediately before the genesis of the
        lineages. If set to False, columns within `population` that
        definitively do not share common ancestry will raise a ValueError.
    progress_wrap : Callable, optional
        Wrapper applied around generation iterator and row generator for final
        phylogeny compilation process.

        Pass tqdm or equivalent to display progress bars.
    seed: int, default 1
        Controls tiebreaking decisions in the algorithm.

        Pass an int for reproducible output across multiple function calls. The
        default value, 1, ensures reproducible output. Pass None to use
        existing RNG context directly.

    Returns
    -------
    typing.List[pd.DataFrame]
        Reconstructed phylogenetic trees with each postprocessor applied, in
        alife standard format.
    """
    with opyt.apply_if_or_value(
        seed,
        RngStateContext,
        contextlib.nullcontext(),
    ):
        return _build_tree_trie_ensemble(
            population=population,
            trie_postprocessors=trie_postprocessors,
            taxon_labels=taxon_labels,
            force_common_ancestry=force_common_ancestry,
            progress_wrap=progress_wrap,
        )
