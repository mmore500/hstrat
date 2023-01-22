import numpy as np

from ...._auxiliary_lib import jit, jit_numpy_bool_t


# implemented as free function (not member) so self param doesn't interfere
# with nopython directive
@jit(nopython=True)
def _discern_referenced_rows(
    parentage_buffer: np.array,
    num_records: int,
    population_size: int,
    below_row: int = 0,
) -> np.array:
    """Return array of indices for all rows at or below `below_row` that
    represent organisms with extant lineages.

    Indices of rows with extinct lineages are not included.
    """

    assert below_row >= 0
    assert num_records >= below_row

    referenced_rows = np.zeros(num_records - below_row, dtype=jit_numpy_bool_t)
    for pop_position in range(population_size):
        idx = num_records - population_size + pop_position
        while (
            idx != parentage_buffer[idx]
            and idx >= below_row
            and not referenced_rows[idx - below_row]
        ):
            referenced_rows[idx - below_row] = True
            idx = parentage_buffer[idx]

        if idx >= below_row:
            referenced_rows[idx - below_row] = True

    return referenced_rows
