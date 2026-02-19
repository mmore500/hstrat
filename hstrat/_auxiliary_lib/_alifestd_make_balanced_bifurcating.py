import itertools as it

import more_itertools as mit
import pandas as pd

from ._alifestd_make_empty import alifestd_make_empty


def alifestd_make_balanced_bifurcating(depth: int) -> pd.DataFrame:
    """Build a perfectly balanced bifurcating tree of given depth.

    Parameters
    ----------
    depth : int
        Depth of the tree, where depth=1 is a single root node.

        - depth=0 -> empty tree (no nodes)
        - depth=1 -> 1 node (root only)
        - depth=2 -> 3 nodes (root + 2 leaves)
        - depth=3 -> 7 nodes (4 leaves)
        - depth=4 -> 15 nodes (8 leaves)

    Returns
    -------
    pd.DataFrame
        Alife-standard phylogeny dataframe with 'id' and 'ancestor_list'
        columns.

    Raises
    ------
    ValueError
        If depth is negative.
    """
    if depth < 0:
        raise ValueError("depth must be non-negative")
    elif depth == 0:
        return alifestd_make_empty()

    ids = [0]
    ancestors = ["[None]"]
    next_id = it.count(1)
    queue = [0]
    for _ in range(depth - 1):
        next_queue = []
        for parent in mit.repeat_each(queue, 2):
            child = next(next_id)
            ids.append(child)
            ancestors.append(f"[{parent}]")
            next_queue.append(child)
        queue = next_queue
    return pd.DataFrame({"id": ids, "ancestor_list": ancestors})
