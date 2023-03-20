import numbers
import typing
import warnings

import alifedata_phyloinformatics_convert as apc
import pandas as pd

from ...._auxiliary_lib import (
    alifestd_is_chronologically_ordered,
    alifestd_reroot_at_id_asexual,
)
from ._estimate_origin_times import estimate_origin_times


def time_calibrate_tree(
    alifestd_df: pd.DataFrame,
    leaf_node_origin_times: typing.Dict[int, numbers.Number],
    negative_origin_time_correction_method: typing.Optional[str] = None,
) -> pd.DataFrame:
    """Time-calibrates a given tree by estimating the origin time of its nodes,
    working backward from phylogenetic depths of leaf nodes using branch_length
    attributes.

    Sets `origin_time` attributes on tree nodes, reroots the tree to the most
    ancient (chronologically) clade, and sets the `branch_length` of the new
    root node to reflect estimated generations elapsed between genesis and the
    MRCA.

    Parameters
    ----------
    tree : pd.DataFrame
        Phylogeny to calibrate, in alife standard format.
    leaf_node_origin_times : dict
        A dictionary that maps the `id` attributes of leaf nodes in the tree
        to their phylogenetic depths since genesis.
    negative_origin_time_correction_method
        : {"truncate", "shift", "rescale"}, optional
        How should negative origin time estimates be corrected?
    """

    if not len(alifestd_df):
        return alifestd_df

    assert "branch_length" in alifestd_df or "edge_length" in alifestd_df
    digraph = apc.alife_dataframe_to_networkx_digraph(
        alifestd_df,
        setup_edge_lengths=True,
    )
    graph = digraph.to_undirected()
    node_origin_times = estimate_origin_times(graph, leaf_node_origin_times)

    new_root_ids = [
        node
        for node in graph.nodes
        # older than or same age as neighbors
        if not any(
            node_origin_times[neighbor] < node_origin_times[node]
            for neighbor in graph.neighbors(node)
        )
    ]
    assert new_root_ids  # guarantee reroot for consistent output columns
    for new_root_id in sorted(
        new_root_ids, key=lambda x: (node_origin_times[x], x), reverse=True
    ):
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

    # could also shift and rescale or just shift,
    # maybe make kwarg option in future
    # for now, just truncate
    min_origin_time = alifestd_df["origin_time"].min()
    if min_origin_time < 0:
        if negative_origin_time_correction_method is None:
            warnings.warn(
                f"""Negative origin time(s) estimated with minimum {
                    min_origin_time
                }; truncating negative origin time(s) to zero. """
                "Set negative_origin_time_correction_method to silence this "
                "warning."
            )
            negative_origin_time_correction_method = "truncate"

        if negative_origin_time_correction_method == "truncate":
            alifestd_df.loc[alifestd_df["origin_time"] < 0, "origin_time"] = 0
        elif negative_origin_time_correction_method == "rescale":
            scale_to = alifestd_df["origin_time"].max()
            shift_by = -min_origin_time
            alifestd_df["origin_time"] += shift_by
            alifestd_df["origin_time"] *= scale_to / (scale_to + shift_by)
        elif negative_origin_time_correction_method == "shift":
            shift_by = -alifestd_df["origin_time"].min()
            alifestd_df["origin_time"] += shift_by
        else:
            assert False, negative_origin_time_correction_method

    assert alifestd_is_chronologically_ordered(alifestd_df)

    return alifestd_df
