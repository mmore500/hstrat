import statistics
import typing

import alifedata_phyloinformatics_convert as apc
import opytional as opyt
import pandas as pd

from ...._auxiliary_lib import (
    BioPhyloTree,
    alifestd_find_root_ids,
    alifestd_make_empty,
    alifestd_validate,
)
from ....genome_instrumentation import HereditaryStratigraphicColumn
from ...population import build_distance_matrix_biopython
from ._append_genesis_organism import append_genesis_organism
from ._time_calibrate_tree import time_calibrate_tree


def build_tree_biopython_distance(
    algo: str,
    population: typing.Sequence[HereditaryStratigraphicColumn],
    estimator: str,
    prior: typing.Union[str, typing.Any],
    taxon_labels: typing.Optional[typing.Iterable],
    force_common_ancestry: bool,
) -> pd.DataFrame:
    """Backend interface to biopython distance-based tree reconstruction
    methods."""

    # biopython doesn't represent empty tree elegantly
    # for simplicity, return early for this special case
    if len(population) == 0:
        return alifestd_make_empty()

    taxon_labels = opyt.or_value(
        taxon_labels,
        [*map(str, range(len(population)))],
    )

    distance_matrix = build_distance_matrix_biopython(
        population,
        estimator,
        prior,
        taxon_labels,
        force_common_ancestry or None,
    )
    constructor = getattr(BioPhyloTree.DistanceTreeConstructor(), algo)
    biopython_tree = (
        BioPhyloTree.BaseTree.Tree()
        if not distance_matrix
        else constructor(distance_matrix)
    )

    # convert, calibrate, and return
    alifestd_df = apc.biopython_tree_to_alife_dataframe(biopython_tree)
    alifestd_df["taxon_label"] = alifestd_df["name"]

    id_lookup = dict(zip(alifestd_df["taxon_label"], alifestd_df["id"]))
    col_lookup = dict(zip(taxon_labels, population))

    leaf_origin_times = {
        id_lookup[taxon_label]: col_lookup[taxon_label].GetNumStrataDeposited()
        - 1
        for taxon_label in taxon_labels
    }
    alifestd_df = time_calibrate_tree(alifestd_df, leaf_origin_times)

    alifestd_df = append_genesis_organism(alifestd_df, mutate=True)

    assert alifestd_validate(alifestd_df)
    assert len(alifestd_find_root_ids(alifestd_df))

    return alifestd_df
