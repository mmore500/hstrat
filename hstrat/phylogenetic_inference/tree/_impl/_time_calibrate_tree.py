import numbers
import typing

import alifedata_phyloinformatics_convert as apc
from iterpop import iterpop as ip
import pandas as pd
import sortedcontainers as sc

from ...._auxiliary_lib import (
    alifestd_is_chronologically_ordered,
    alifestd_reroot_at_id_asexual,
    BioPhyloTree,
)
from ._estimate_origin_times import estimate_origin_times


def time_calibrate_tree(
    alifestd_df: pd.DataFrame,
    leaf_node_origin_times: typing.Dict[int, numbers.Number],
) -> pd.DataFrame:
    """Time-calibrates a given tree by estimating the origin time of its nodes, by working backward from phylogenetic depths of leaf nodes using branch_length attributes of tree nodes.

    Sets `origin_time` attributes on tree nodes, reroots the tree to the most ancient (chronologically) clade, and sets the `branch_length` of the new root node to reflect estimated generations elapsed between genesis and the MRCA.

    Parameters
    ----------
    tree : pd.DataFrame
        Phylogeny to calibrate, in alife standard format.
    leaf_node_origin_times : dict
        A dictionary that maps the `id` attributes of leaf nodes in the tree
        to their phylogenetic depths since genesis.
    """

    if not len(alifestd_df):
        return alifestd_df

    assert "branch_length" in alifestd_df or "edge_length" in alifestd_df
    digraph = apc.alife_dataframe_to_networkx_digraph(
        alifestd_df,
        setup_edge_lengths=True,
    )
    graph = digraph.to_undirected()
    # assert len(graph)
    node_origin_times = estimate_origin_times(graph, leaf_node_origin_times)

    new_root_ids = [
        node
        for node in graph.nodes
        # older than or same age as neighbors
        if not any(
            node_origin_times[neighbor] <= node_origin_times[node]
            for neighbor in graph.neighbors(node)
        )
    ]
    assert new_root_ids  # guarantee reroot for consistent output columns
    for new_root_id in new_root_ids:
        alifestd_df = alifestd_reroot_at_id_asexual(
            alifestd_df.drop(
                ["branch_length", "edge_length"],
                axis="columns",
                errors="ignore",
            ),
            new_root_id,
            mutate=True,
        )

    alifestd_df["origin_time"] = alifestd_df["id"].map(node_origin_times)

    assert alifestd_is_chronologically_ordered(alifestd_df)

    return alifestd_df
