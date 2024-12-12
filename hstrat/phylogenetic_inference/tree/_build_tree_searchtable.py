import typing

import opytional as opyt
import pandas as pd

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ._impl import build_tree_searchtable_python

try:
    from ._impl._build_tree_searchtable_cpp import build_tree_searchtable_cpp
except ImportError:  # pragma: no cover
    build_tree_searchtable_cpp = None


def build_tree_searchtable(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    progress_wrap: typing.Optional[typing.Callable] = None,
    force_common_ancestry: bool = False,
    use_impl: typing.Literal["cpp", "python", None] = None,
) -> pd.DataFrame:
    """Estimate the phylogenetic history among hereditary stratigraphic
    artifacts by building a trie (a.k.a. prefix tree) of their differentiae
    records.

    In contrast to `build_tree_trie`, this function applies a more efficient
    algorithm that collapses away inner nodes corresponding to dropped ranks
    to prevent exponential time complexity from "wildcard" (i.e., missing)
    differentiae when reconstructing the phylogeny.

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
        How should columns that definitively share no common ancestry be
        handled?

        If set to True, treat columns with no common ancestry as if they
        shared a common ancestor immediately before the genesis of the
        lineages. If set to False, columns within `population` that
        definitively do not share common ancestry will raise a ValueError.
    progress_wrap : Callable, optional
        Pass tqdm or equivalent to display a progress bar.
    use_impl : {'cpp', 'python', None}, optional
        Which implementation to use.

        If None, the best available implementation will be used.
        If 'cpp', the C++ implementation will be used.
        If 'python', the Python implementation will be used.

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

    Uses a more efficient tabular, rather than node-and-pointer, underlying trie
    representation. Two trie structures are maintained: one for building the
    trie, and one for searching the trie. The "search" trie structure is
    reconfigurable to collapse portions of the trie for efficient search. The
    "build" trie structure is used to record the original structure of the trie.

    See Also
    --------
    build_tree_trie : Naive trie-based phylogenetic reconstruction algorithm.
    """
    try:
        build_tree_searchtable_impl = {
            "cpp": build_tree_searchtable_cpp,
            "either": opyt.or_value(
                build_tree_searchtable_cpp,
                build_tree_searchtable_python,
            ),
            "python": build_tree_searchtable_python,
        }[opyt.or_value(use_impl, "either")]
    except KeyError:
        raise ValueError(
            f"Invalid value {use_impl} for `use_impl`. "
            "Expected one of 'cpp', 'python', or None.",
        )

    if build_tree_searchtable_impl is None:  # pragma: no cover
        raise ImportError(
            f"build_tree_searchtable impl '{use_impl}' is unavailable.",
        )

    return build_tree_searchtable_impl(
        population,
        taxon_labels,
        progress_wrap,
        force_common_ancestry,
    )
