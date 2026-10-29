import numpy as np

from ._jit import jit


@jit(nopython=True)
def calc_lineage_affine_with_contiguous_ids(
    ancestor_ids: np.ndarray,
    multipliers: np.ndarray,
    addends: np.ndarray,
) -> np.ndarray:
    """Evaluate affine recurrence down each lineage, from roots to tips.

    Calculates `result[i] = multipliers[i] * result[ancestor_ids[i]] +
    addends[i]`, with `result[i] = addends[i]` for roots.

    Assumes that each organism's ancestor id is located at the index position
    in `ancestor_ids` corresponding to its own id, and that ancestors precede
    descendants (i.e., topological sorting).
    """
    result = np.empty(len(ancestor_ids), dtype=np.float64)
    for id_, ancestor_id in enumerate(ancestor_ids):
        if ancestor_id == id_:
            result[id_] = addends[id_]
        else:
            assert ancestor_id < id_
            result[id_] = multipliers[id_] * result[ancestor_id] + addends[id_]
    return result
