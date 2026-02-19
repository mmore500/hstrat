import itertools as it

import pandas as pd

from ._alifestd_make_empty import alifestd_make_empty


def alifestd_make_comb(n_leaves: int) -> pd.DataFrame:
    r"""Build a comb/caterpillar tree with `n_leaves` leaves.

    Internal nodes: 0, 2, 4, ...
    Leaves: 1, 3, 5, ...

    Parameters
    ----------
    n_leaves : int
        Number of leaf nodes in the resulting tree.

    Returns
    -------
    pd.DataFrame
        Alife-standard phylogeny dataframe with 'id' and 'ancestor_list'
        columns.

    Raises
    ------
    ValueError
        If n_leaves is negative.
    """
    if n_leaves < 0:
        raise ValueError("n_leaves must be non-negative")
    if n_leaves == 0:
        return alifestd_make_empty()

    ids = []
    ancestors = []
    node_id = it.count()
    root = next(node_id)
    ids.append(root)
    ancestors.append("[None]")
    parent = root
    for i in range(n_leaves - 1):
        child_leaf = next(node_id)
        ids.append(child_leaf)
        ancestors.append(f"[{parent}]")
        child_internal = next(node_id)
        ids.append(child_internal)
        ancestors.append(f"[{parent}]")
        parent = child_internal
    return pd.DataFrame({"id": ids, "ancestor_list": ancestors})
