import typing

import pandas as pd

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._impl import build_tree_biopython_distance


def build_tree_upgma(
    population: typing.Sequence[HereditaryStratigraphicColumn],
    estimator: str,
    prior: typing.Union[str, typing.Any],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    force_common_ancestry: bool = False,
    negative_origin_time_correction_method: typing.Optional[str] = None,
) -> pd.DataFrame:
    """Estimate the phylogenetic history among hereditary stratigraphic
    columns by using the "unweighted pair group method with unweighted means"
    (UPGMA) distance-based reconstruction method.

    This phylogenetic reconstruction approach is generally unfavorable, incuring
    `O(n^2)` runtime complexity and providing reconstructions that ocassionally
    conflict with the hereditary stratigraphic record.

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
    negative_origin_time_correction_method
        : {"truncate", "shift", "rescale"}, optional
        How should negative origin time estimates be corrected?

    Returns
    -------
    pd.DataFrame
        The reconstructed phylogenetic tree in alife standard format.
    """
    return build_tree_biopython_distance(
        "upgma",
        population,
        estimator,
        prior,
        taxon_labels,
        force_common_ancestry,
        negative_origin_time_correction_method,
    )
