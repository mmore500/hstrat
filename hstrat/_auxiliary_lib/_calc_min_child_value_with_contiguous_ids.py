import numpy as np


def calc_min_child_value_with_contiguous_ids(
    ancestor_ids: np.ndarray,
    values: np.ndarray,
    fill_value: float = np.inf,
) -> np.ndarray:
    """Calculate minimum of `values` among each node's children.

    Nodes without children are assigned `fill_value`.

    Assumes that each organism's ancestor id is located at the index position
    in `ancestor_ids` corresponding to its own id.
    """
    ancestor_ids = np.asarray(ancestor_ids, dtype=np.intp)
    values = np.asarray(values, dtype=np.float64)
    is_root = ancestor_ids == np.arange(len(ancestor_ids))
    result = np.full(len(ancestor_ids), np.inf, dtype=np.float64)
    np.minimum.at(result, ancestor_ids[~is_root], values[~is_root])
    has_children = np.bincount(
        ancestor_ids[~is_root], minlength=len(ancestor_ids)
    ).astype(bool)
    result[~has_children] = fill_value
    return result
