import typing

from iterpop import iterpop as ip
import pandas as pd

from . import trie_postprocess
from ..._auxiliary_lib import (
    HereditaryStratigraphicArtifact,
    alifestd_make_empty,
)
from ._build_tree_trie_ensemble import build_tree_trie_ensemble


def build_tree_trie(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    force_common_ancestry: bool = False,
    progress_wrap: typing.Callable = lambda x: x,
    seed: typing.Optional[int] = 1,
    bias_adjustment: typing.Union[str, object, None] = None,
) -> pd.DataFrame:
    """Estimate the phylogenetic history among hereditary stratigraphic
    columns by building a trie (a.k.a. prefix tree) of the differentia
    sequences of hereditary stratigraphic artifacts within a population.

    Exhibits time complexity at most `O(nlog(n))` for population size `n`.

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
        Pass tqdm or equivalent to display progress bars.
    seed : int, default 1
        Controls tiebreaking decisions in the algorithm.

        Pass an int for reproducible output across multiple function calls. The
        default value, 1, ensures reproducible output. Pass None to use global
        RNG context.
    bias_adjustment : "sample_ancestral_rollbacks" or prior, optional
        How should bias toward overestimation of relatedness due to differentia
        collisions be corrected for?

        If "sample_ancestral_rollbacks", the trie topology will be adjusted as
        if the expected number of collisions had occured. Targets for
        "unzipping" to reverse the effect of a speculated collision are
        chosen randomly from within the tree. See
        `SampleAncestralRollbacksTriePostprocessor` for details.

        If a prior functor is passed, the origin time for each trie node will
        be calculated as the expected origin time over the distribution of
        possible differentia collisions. Correction recursively takes into
        account the possibility of multiple collisions. See
        `hstrat.phylogenetic_inference.priors` for available prior
        distributions. A custom prior distribution may also be supplied. See
        `AssignOriginTimeExpectedValueTriePostprocessor` for details.

        If a prior functor is passed, correction for guaranteed-spurious
        collision between most-recent strata will also be performed. See
        `PeelBackConjoinedLeavesTriePostprocessor` for details.

        If None, no correction will be performed. The origin time for each trie
        node will be assigned using a naive strategy, calculated as the average
        of the node's rank and the minimum rank among its children. See
        `AssignOriginTimeNaiveTriePostprocessor` for details.

    Returns
    -------
    pd.DataFrame
        The reconstructed phylogenetic tree in alife standard format.

    Notes
    -----
    Unifurcations in the reconstructed tree are collapsed.

    However, polytomies are not resolved. In addition to any true polytomies,
    ancestry sequences that cannot be resolved due to missing information
    appear as polytomies in the generated reconstruction. Therefore, polytomies
    are generally overrepresented in reconstructions, especially when low
    hereditary stratigraphic resolution is available. If overestimation of
    polytomies is problematic, external tools can be used to decompose
    polytomies into arbitrarily-arranged bifurcations.
    """

    # for simplicity, return early for this special case
    if len(population) == 0:
        return alifestd_make_empty()

    if bias_adjustment is None:
        trie_postprocessor = (
            trie_postprocess.AssignOriginTimeNaiveTriePostprocessor()
        )
    elif (
        isinstance(bias_adjustment, str)
        and bias_adjustment == "sample_ancestral_rollbacks"
    ):

        trie_postprocessor = trie_postprocess.CompoundTriePostprocessor(
            postprocessors=[
                trie_postprocess.SampleAncestralRollbacksTriePostprocessor(
                    seed=1
                ),
                trie_postprocess.AssignOriginTimeNaiveTriePostprocessor(),
            ],
        )

    else:
        trie_postprocessor = trie_postprocess.CompoundTriePostprocessor(
            postprocessors=[
                trie_postprocess.PeelBackConjoinedLeavesTriePostprocessor(),
                trie_postprocess.AssignOriginTimeExpectedValueTriePostprocessor(
                    prior=bias_adjustment,
                ),
            ],
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
