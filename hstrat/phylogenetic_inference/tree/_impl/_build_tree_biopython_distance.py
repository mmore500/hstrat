import statistics
import typing

import Bio.Phylo.TreeConstruction as BioPhyloTree
import alifedata_phyloinformatics_convert as apc
import opytional as opyt
import pandas as pd

from ....genome_instrumentation import HereditaryStratigraphicColumn
from ...population import build_distance_matrix_biopython


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

    def iter_leaf_col_zip():
        col_lookup = dict(zip(taxon_labels, population))
        yield from (
            (leaf_node, col_lookup[leaf_node.name])
            for leaf_node in biopython_tree.get_terminals()
        )

    if population:
        # set up length for branch subtending global mrca
        base_branch_est = statistics.mean(
            extant_col.GetNumStrataDeposited()
            - 1
            - biopython_tree.distance(leaf_node)
            for leaf_node, extant_col in iter_leaf_col_zip()
        )
        # assert base_branch_est >= 0
        biopython_tree.root.branch_length = base_branch_est
        # print(base_branch_est, [
        #     (biopython_tree.distance(leaf_node), extant_col.GetNumStrataDeposited())
        #     for leaf_node, extant_col in iter_leaf_col_zip()
        # ])

    # convert and return
    alifestd_df = apc.biopython_tree_to_alife_dataframe(biopython_tree)
    alifestd_df["taxon_label"] = alifestd_df["name"]
    return alifestd_df
