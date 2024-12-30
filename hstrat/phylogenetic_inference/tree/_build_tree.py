import typing

from packaging import version
import pandas as pd

from ..._auxiliary_lib import (
    HereditaryStratigraphicArtifact,
    get_hstrat_version,
)
from ..priors._ArbitraryPrior import ArbitraryPrior
from ._build_tree_trie import build_tree_trie


def build_tree(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    version_pin: str,
    taxon_labels: typing.Optional[typing.Iterable] = None,
    force_common_ancestry: bool = False,
    progress_wrap: typing.Callable = lambda x: x,
) -> pd.DataFrame:
    """Estimate the phylogenetic history among hereditary stratigraphic
    columns.

    This function provides a generic interface that directs to an underlying
    implementation, chosen for flexibility and robustness across reconstruction
    scenarios. The underlying implementation may be revised in future releases
    of the software.

    The current implementation delegates to `build_tree_trie`.

    Parameters
    ----------
    population: Sequence[HereditaryStratigraphicArtifact]
        Hereditary stratigraphic columns corresponding to extant population members.

        Each member of population will correspond to a unique leaf node in the
        reconstructed tree.
    version_pin: str
        How should calls to this function resolve in future hstrat releases?

        To prevent future releases from silently substituting the underlying
        reconstruction algorithm, hardcode the current version of hstrat here.
        To automatically track any future library updates, pass
        `hstrat.__version__` here.

        Some effort will be made to maintain historical implementations to
        support prior version pins. However, indefinite support is not
        guaranteed for hard version pins; old version pins may eventually raise
        `DeprecationWarning` or `ValueError`. Where reasonable, consider
        directly calling an implementing tree building method instead.
    taxon_labels: Optional[Iterable], optional
        How should leaf nodes representing extant hereditary stratigraphic
        columns be named?

        Label order should correspond to the order of corresponding hereditary
        stratigraphic columns within `population`. If None, taxons will be
        named according to their numerical index.
    force_common_ancestry: bool, optional
        How should columns that definitively share no common ancestry be
        handled?

        If set to True, treat columns with no common ancestry as if they
        shared a common ancestor immediately before the genesis of the
        lineages. If set to False, columns within `population` that
        definitively do not share common ancestry will raise a ValueError.
    progress_wrap : Callable, optional
        Pass tqdm or equivalent to display progress bars.

    Returns
    -------
    pd.DataFrame
        The reconstructed phylogenetic tree in alife standard format.

    Raises
    ------
    ValueError
        If the specified `version_pin` is higher than the current version of
        hstrat.
    """

    if version.parse(version_pin) > version.parse(get_hstrat_version()):
        raise ValueError(f"unsupported verison {version_pin}")

    return build_tree_trie(
        population,
        taxon_labels,
        force_common_ancestry=force_common_ancestry,
        progress_wrap=progress_wrap,
        bias_adjustment=ArbitraryPrior(),
    )
