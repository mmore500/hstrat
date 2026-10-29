import typing

import numpy as np

from ._jit import jit


@jit(nopython=True)
def _accumulate_num_collapsed_unifurcations_jit(
    ancestor_ids: np.ndarray,
    num_collapsed: np.ndarray,
) -> np.ndarray:
    """Implementation detail for `accumulate_num_collapsed_unifurcations`."""
    n = len(ancestor_ids)
    ref_counts = np.zeros(n, dtype=np.uint8)
    for ancestor_id in ancestor_ids:
        # cap to prevent overflow
        ref_counts[ancestor_id] = min(ref_counts[ancestor_id] + 1, 2)

    # is unifurcation, excluding roots (which are never collapsed)
    is_removed = np.zeros(n, dtype=np.bool_)
    for id_ in range(n):
        is_removed[id_] = ref_counts[id_] == 1 and ancestor_ids[id_] != id_

    # for removed nodes, holds count to pass on to descendants
    result = np.zeros(n, dtype=np.uint32)
    for id_ in range(n):
        ancestor_id = ancestor_ids[id_]
        assert ancestor_id <= id_
        inherited = result[ancestor_id] if is_removed[ancestor_id] else 0
        result[id_] = inherited + num_collapsed[id_] + int(is_removed[id_])

    return result


def accumulate_num_collapsed_unifurcations(
    ancestor_ids: np.ndarray,
    num_collapsed: typing.Optional[np.ndarray] = None,
) -> np.ndarray:
    """Calculate number of unifurcations that will be collapsed away between
    each node and its nearest non-unifurcating ancestor.

    Counts are tallied in addition to any already-collapsed unifurcations
    recorded in `num_collapsed`. Uses the same unifurcation criteria as
    `phyloframe.legacy.alifestd_collapse_unifurcations` (i.e., roots are
    never collapsed).

    Parameters
    ----------
    ancestor_ids : np.ndarray
        Ancestor id of each node.

        Ids must be contiguous and topologically sorted.
    num_collapsed : np.ndarray, optional
        Number of unifurcations previously collapsed away above each node.

        If None, assumed zero.

    Returns
    -------
    np.ndarray
        Updated counts, as `np.uint32`.

        Values for nodes that are themselves unifurcations are not meaningful,
        as these nodes are removed by unifurcation collapse.
    """
    ancestor_ids = np.asarray(ancestor_ids, dtype=np.uint64)
    if num_collapsed is None:
        num_collapsed = np.zeros(len(ancestor_ids), dtype=np.uint32)
    num_collapsed = np.asarray(num_collapsed, dtype=np.uint32)
    return _accumulate_num_collapsed_unifurcations_jit(
        ancestor_ids, num_collapsed
    )
