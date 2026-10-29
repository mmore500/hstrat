import numpy as np

from ._jit import jit


@jit(nopython=True)
def calc_lineage_max_with_contiguous_ids(
    ancestor_ids: np.ndarray,
    values: np.ndarray,
) -> np.ndarray:
    """Calculate maximum value over each node and its ancestors.

    NaN values propagate as NaN for that node, but are skipped when
    calculating descendants' maxima.

    Assumes that each organism's ancestor id is located at the index position
    in `ancestor_ids` corresponding to its own id, and that ancestors precede
    descendants (i.e., topological sorting).
    """
    result = values.astype(np.float64)
    for id_, ancestor_id in enumerate(ancestor_ids):
        if ancestor_id == id_:
            continue
        assert ancestor_id < id_
        if np.isnan(result[id_]):
            continue
        # skip NaN ancestor, but carry on through its own ancestors
        while np.isnan(result[ancestor_id]):
            if ancestor_ids[ancestor_id] == ancestor_id:
                break
            ancestor_id = ancestor_ids[ancestor_id]
        if not np.isnan(result[ancestor_id]):
            result[id_] = max(result[id_], result[ancestor_id])
    return result
