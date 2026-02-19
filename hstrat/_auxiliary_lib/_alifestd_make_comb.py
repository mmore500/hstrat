import itertools as it

import pandas as pd

from ._alifestd_make_empty import alifestd_make_empty


def alifestd_make_comb(n_leaves: int) -> pd.DataFrame:
    r"""Build a comb/caterpillar tree with `n_leaves` leaves.

    Structure (e.g., n_leaves=4)::

              0
             / \
            1   2
               / \
              3   4
                 / \
                5   6

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
    elif n_leaves == 0:
        return alifestd_make_empty()

    node_counter = it.count()
    ids, ancestors = [next(node_counter)], ["[None]"]
    (parent,) = ids
    for _ in range(n_leaves - 1):
        child_leaf = next(node_counter)
        ids.append(child_leaf)
        ancestors.append(f"[{parent}]")
        child_internal = next(node_counter)
        ids.append(child_internal)
        ancestors.append(f"[{parent}]")
        parent = child_internal
    return pd.DataFrame({"id": ids, "ancestor_list": ancestors})
