import pandas as pd


def alifestd_make_comb(n_leaves: int) -> pd.DataFrame:
    r"""Build a comb/caterpillar tree with `n_leaves` leaves.

    Structure (e.g. n_leaves=4):

    .. code-block:: text

              0
             / \
            1   2
               / \
              3   4
                 / \
                5   6

    Internal nodes: 0, 2, 4, ...  Leaves: 1, 3, 5, 6

    Parameters
    ----------
    n_leaves : int
        Number of leaf nodes in the resulting tree.

    Returns
    -------
    pd.DataFrame
        Alife-standard phylogeny dataframe with 'id' and 'ancestor_list'
        columns.
    """
    ids = []
    ancestors = []
    node_id = 0
    ids.append(node_id)
    ancestors.append("[None]")
    for i in range(n_leaves - 1):
        parent = node_id
        node_id += 1
        ids.append(node_id)
        ancestors.append(f"[{parent}]")
        node_id += 1
        ids.append(node_id)
        ancestors.append(f"[{parent}]")
    return pd.DataFrame({"id": ids, "ancestor_list": ancestors})
