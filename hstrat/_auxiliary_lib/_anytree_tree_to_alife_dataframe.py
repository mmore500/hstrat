# copied from https://github.com/mmore500/alifedata-phyloinformatics-convert/blob/9287db7c101604cf49df16617fb32a632122fbd9/alifedata_phyloinformatics_convert/anytree_tree_to_alife_dataframe.py
# with recursive iterators swapped for iterative implementatins


import anytree
from nanto import isanan
import opytional as opyt
import pandas as pd

from ._AnyTreeFastLevelOrderIter import AnyTreeFastLevelOrderIter
from ._AnyTreeFastPreOrderIter import AnyTreeFastPreOrderIter


def anytree_tree_to_alife_dataframe(
    tree: anytree.AnyNode,
) -> pd.DataFrame:
    """Convert a anytree tree to a dataframe formatted to the
    artificial life community data format standards.

    The following Node object attributes will automatically be exported to
    dataframe columns, if available:
        * edge_length,
        * id,
        * label,
        * name,
        * destruction_time,
        * origin_time, and
        * taxon_label.

    Parameters
    ----------
    tree:
        anytree tree to convert.
    """

    # set up node origin times if any edge lengths set
    if any(
        getattr(node, "edge_length", None) is not None
        for node in AnyTreeFastPreOrderIter(tree)
    ):
        if not hasattr(tree, "origin_time"):
            tree.origin_time = opyt.or_value(
                getattr(tree, "edge_length", None), 0
            )
        else:
            assert tree.origin_time is not None
        for node in AnyTreeFastLevelOrderIter(tree):
            parent = node.parent
            if parent is not None and not hasattr(node, "origin_time"):
                if None not in (
                    getattr(parent, "origin_time", None),
                    getattr(node, "edge_length", None),
                ) and (
                    not isanan(parent.origin_time)
                    and not isanan(node.edge_length)
                ):
                    node.origin_time = parent.origin_time + node.edge_length

    # attach ids to nodes, if needed
    for fallback_id, node in enumerate(AnyTreeFastLevelOrderIter(tree)):
        if not hasattr(node, "id"):
            node.id = fallback_id
        else:
            assert isinstance(node.id, int)

    return pd.DataFrame.from_records(
        [
            {
                "id": node.id,
                "ancestor_list": f"[{opyt.apply_if(node.parent, lambda x: x.id)}]",
                "edge_length": getattr(node, "edge_length", None),
                "label": getattr(node, "label", None),
                "name": getattr(node, "name", None),
                "origin_time": getattr(node, "origin_time", None),
                "destruction_time": getattr(node, "destruction_time", None),
                "taxon_label": getattr(node, "taxon_label", None),
            }
            for node in AnyTreeFastLevelOrderIter(tree)
        ]
    ).dropna(axis=1, how="all")
