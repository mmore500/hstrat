import numpy as np

from ._jit import jit


@jit(nopython=True)
def unfurl_lineage_with_contiguous_ids(
    ancestor_ids: np.ndarray, leaf_id: int
) -> np.ndarray:
    """List leaf id and its ancestor id sequence through tree root.

    Assumes that each organism's ancestor id is located at the index position
    in `ancestor_ids` corresponding to its own id.
    """
    id_ = np.uint64(leaf_id)  # not sure why this type coercion is necessary
    ancestor_ids = ancestor_ids.astype(np.uint64)
    res = list()
    while True:
        res.append(id_)
        next_id = ancestor_ids[id_]
        if id_ == next_id:
            break
        id_ = next_id

    return np.array(res, dtype=np.uint64)
