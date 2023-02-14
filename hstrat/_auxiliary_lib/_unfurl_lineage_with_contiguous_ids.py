import numpy as np

from ._jit import jit


@jit(nopython=True)
def unfurl_lineage_with_contiguous_ids(
    ancestor_ids: np.array, leaf_id: int
) -> np.array:
    """List leaf id and its ancestor id sequence through tree root.

    Assumes that each organism's ancestor id is located at the index position
    in `ancestor_ids` corresponding to its own id.
    """
    id_ = leaf_id
    res = list()
    while True:
        res.append(id_)
        next_id = ancestor_ids[id_]
        if id_ == next_id:
            break
        id_ = next_id

    return np.array(res)
