import pandas as pd


def alifestd_make_balanced_bifurcating(depth: int) -> pd.DataFrame:
    """Build a perfectly balanced bifurcating tree of given depth.

    Parameters
    ----------
    depth : int
        Depth of the tree, where depth=1 is a single root node.

        - depth=1 -> 1 node (root only)
        - depth=2 -> 3 nodes (root + 2 leaves)
        - depth=3 -> 7 nodes (4 leaves)
        - depth=4 -> 15 nodes (8 leaves)

    Returns
    -------
    pd.DataFrame
        Alife-standard phylogeny dataframe with 'id' and 'ancestor_list'
        columns.
    """
    ids = [0]
    ancestors = ["[None]"]
    next_id = 1
    queue = [0]
    for _ in range(depth - 1):
        next_queue = []
        for parent in queue:
            for _ in range(2):
                ids.append(next_id)
                ancestors.append(f"[{parent}]")
                next_queue.append(next_id)
                next_id += 1
        queue = next_queue
    return pd.DataFrame({"id": ids, "ancestor_list": ancestors})
