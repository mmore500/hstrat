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

    ids = [0]
    ancestors = ["[None]"]
    for parent, child_internal in it.pairwise(range(0, 2 * n_leaves, 2)):
        child_leaf = child_internal - 1
        ids.extend([child_leaf, child_internal])
        ancestors.extend([f"[{parent}]", f"[{parent}]"])
    return pd.DataFrame({"id": ids, "ancestor_list": ancestors})
