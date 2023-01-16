import collections
import typing

import numba as nb
import numpy as np
import pandas as pd

from ._compile_phylogeny_from_lineage_iters import (
    compile_phylogeny_from_lineage_iters,
)


# implemented as free function (not member) so self param doesn't interfere
# with nopython directive
# could refactor to use iter_lineage below, but not sure if would affect perf
@nb.jit(nopython=True)
def _discern_referenced_row_indices(
    parentage_buffer: np.array, num_records: int, population_size: int
) -> np.array:

    capacity = len(parentage_buffer)

    # idea: might be able to speed this up with some kind of binary search
    # if we also stored generation as a column
    visited_row_idxs = set()
    for sought_pop_position in range(population_size):
        first_occurence_idx = capacity - num_records + sought_pop_position
        assert (
            abs(parentage_buffer[first_occurence_idx, 0])
            == sought_pop_position
        )
        sought_pop_position = parentage_buffer[first_occurence_idx, 0]

        for row_idx in range(first_occurence_idx, capacity):
            if parentage_buffer[row_idx, 0] == sought_pop_position:
                if row_idx in visited_row_idxs:
                    break
                else:
                    visited_row_idxs.add(row_idx)
                    sought_pop_position = parentage_buffer[row_idx, 1]

    return np.sort(np.array(list(visited_row_idxs)))


@nb.jit(nopython=True)
def _iter_lineage(
    parentage_buffer: np.array,
    num_records: int,
    population_size: int,
    sought_pop_position: int,
) -> typing.Iterable[int]:

    capacity = len(parentage_buffer)
    first_occurence_idx = capacity - num_records + sought_pop_position
    assert abs(parentage_buffer[first_occurence_idx, 0]) == sought_pop_position
    sought_pop_position = parentage_buffer[first_occurence_idx, 0]

    for row_idx in range(first_occurence_idx, capacity):
        if parentage_buffer[row_idx, 0] == sought_pop_position:
            yield capacity - row_idx
            sought_pop_position = parentage_buffer[row_idx, 1]


class GarbageCollectingPhyloTracker:

    _generations_elapsed: int
    _population_size: int
    _num_records: int
    _parentage_buffer: np.array  # [int]

    # parentage_buffer:
    #                        col 0                col 1
    #                 +------------------+---------------------+
    #  *gen 0*        | org_pop_position | parent_pop_position |
    #                 | org_pop_position | parent_pop_position |
    #
    #                 ...
    #  *gen 1*        | org_pop_position | parent_pop_position |
    #                 | org_pop_position | parent_pop_position |
    #
    #                 ...
    #                 | org_pop_position | parent_pop_position |
    # num_records --> | UNINITIALIZED    | UNINITIALIZED       |
    #                 | UNINITIALIZED    | UNINITIALIZED       |
    #                 | UNINITIALIZED    | UNINITIALIZED       |
    #
    #                 ...
    #                 | UNINITIALIZED    | UNINITIALIZED       |
    #                 +------------------+---------------------+
    #
    # notes:
    # * rows correspond to a single individual in the evolutionary simulation
    #   (i.e., an occupant of a particular population position at a single
    #    generation)
    # * parentage buffer works like a std::vector in C++ in the y (# rows)
    #   direction: extra, unused rows are allocated (but rows past num_records
    #   are empty); when space runs out, the buffer row count is grown 2x
    # * number of rows for each generation will decrease below population_size
    #   as rows corresponding to individuals without extant ancestors are
    #   garbage collected
    # * to ensure that generations can be distinguished, pop positions are
    #   stored with alternating sign
    # * buffer grows from bottom, not top (diagram above should be reversed)
    #   ... this ensures that population positions within a generation are
    #   encountered in strictly ascending order while iterating backwards in
    #   time

    def __init__(
        self: "GarbageCollectingPhyloTracker",
        population_size: int,
        initial_buffer_size: typing.Optional[int] = None,
        share_common_ancestor: bool = True,
    ) -> None:
        if initial_buffer_size is None:
            initial_buffer_size = 10 * population_size

        assert population_size
        assert initial_buffer_size >= population_size + share_common_ancestor

        self._generations_elapsed = 1 + share_common_ancestor
        self._population_size = population_size
        self._parentage_buffer = np.empty(
            (initial_buffer_size, 2),
            dtype=np.min_scalar_type(-population_size + 1),
        )
        self._num_records = population_size + share_common_ancestor

        if share_common_ancestor:
            self._parentage_buffer[-1, :] = [-0, 0]
            self._parentage_buffer[-1 - population_size : -1, 0] = np.arange(
                population_size
            )
            self._parentage_buffer[-1 - population_size : -1, 1] = -0
        else:
            self._parentage_buffer[-population_size:, 0] = np.negate(
                np.arange(population_size)
            )
            self._parentage_buffer[-population_size:, 1] = population_size - 1

    def _GetBufferCapacity(self: "GarbageCollectingPhyloTracker") -> int:
        return self._parentage_buffer.shape[0]

    def _MaybeGarbageCollect(
        self: "GarbageCollectingPhyloTracker", num_to_insert: int
    ) -> None:

        if self._num_records + num_to_insert >= self._GetBufferCapacity():
            referenced_indices = _discern_referenced_row_indices(
                self._parentage_buffer,
                self._num_records,
                self._population_size,
            )

            # condense non-garbage-collected rows to rear of buffer
            self._parentage_buffer[
                self._GetBufferCapacity() - len(referenced_indices) :
            ] = self._parentage_buffer[referenced_indices]
            self._num_records = len(referenced_indices)

    def _MaybeGrowBuffer(
        self: "GarbageCollectingPhyloTracker", num_to_insert: int
    ) -> None:
        while self._num_records + num_to_insert >= self._GetBufferCapacity():
            new_buffer = np.empty(
                (
                    int(self._GetBufferCapacity() * 1.5),
                    self._parentage_buffer.shape[1],
                ),
                dtype=self._parentage_buffer.dtype,
            )
            new_buffer[-self._GetBufferCapacity() :] = self._parentage_buffer
            self._parentage_buffer = new_buffer

    def ElapseGeneration(
        self: "GarbageCollectingPhyloTracker",
        parent_idxs: typing.List[int],
    ) -> None:

        assert self._population_size == len(parent_idxs)

        # if elements will overflow buffer, try garbage collecting
        self._MaybeGarbageCollect(self._population_size)
        # if garbage collecting didn't make enough space, increase buffer size
        self._MaybeGrowBuffer(self._population_size)

        assert self._num_records < self._GetBufferCapacity()

        end_row = self._GetBufferCapacity() - self._num_records
        begin_row = end_row - self._population_size
        self._parentage_buffer[begin_row:end_row, 0] = np.arange(
            0, -self._population_size, -1
        )
        self._parentage_buffer[begin_row:end_row, 1] = parent_idxs

        # to ensure that generations can be distinguished, pop positions are
        # stored with alternating sign
        if self._generations_elapsed % 2:
            self._parentage_buffer[begin_row:end_row, :] = np.negative(
                self._parentage_buffer[begin_row:end_row, :]
            )

        self._generations_elapsed += 1
        self._num_records += self._population_size

    def CompilePhylogeny(
        self: "GarbageCollectingPhyloTracker",
    ) -> pd.DataFrame:
        return compile_phylogeny_from_lineage_iters(
            _iter_lineage(
                self._parentage_buffer,
                self._num_records,
                self._population_size,
                pop_position,
            )
            for pop_position in range(self._population_size)
        )
