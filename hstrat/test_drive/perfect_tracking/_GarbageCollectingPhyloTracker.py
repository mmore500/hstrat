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
def _discern_referenced_rows(
    parentage_buffer: np.array, num_records: int, population_size: int
) -> np.array:

    # idea: might be able to speed this up with some kind of binary search
    # if we also stored generation as a column
    referenced_rows = np.zeros(num_records, dtype=nb.types.bool_)
    for pop_position in range(population_size):
        idx = num_records - population_size + pop_position

        while idx != parentage_buffer[idx] and not referenced_rows[idx]:
            referenced_rows[idx] = True
            idx = parentage_buffer[idx]

        referenced_rows[idx] = True

    return referenced_rows


@nb.jit(nopython=True)
def _iter_lineage(
    parentage_buffer: np.array,
    num_records: int,
    population_size: int,
    pop_position: int,
) -> typing.Iterable[int]:

    idx = num_records - population_size + pop_position

    while True:
        yield idx
        if idx == parentage_buffer[idx]:
            break
        idx = parentage_buffer[idx]


class GarbageCollectingPhyloTracker:

    _population_size: int
    _num_records: int
    _parentage_buffer: np.array  # [int]

    # parentage_buffer:
    #
    #                 +----------------+
    #  *gen 0*        | parent_row_idx |
    #                 | parent_row_idx |
    #
    #                 ...
    #  *gen 1*        | parent_row_idx |
    #                 | parent_row_idx |
    #
    #                 ...
    #                 | parent_row_idx |
    # num_records --> | UNINITIALIZED  |
    #                 | UNINITIALIZED  |
    #                 | UNINITIALIZED  |
    #
    #                 ...
    #                 | UNINITIALIZED  |
    #                 +----------------+
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
    # * self-loop parent_row_idx's denotes no parent (i.e., lineage begin)

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

        self._population_size = population_size
        self._parentage_buffer = np.empty(
            initial_buffer_size,
            dtype=np.int32,
        )
        self._num_records = population_size + share_common_ancestor

        if share_common_ancestor:
            self._parentage_buffer[0] = 0
            self._parentage_buffer[1 : population_size + 1] = 0
        else:
            self._parentage_buffer[:population_size, 0] = np.arange(
                population_size
            )

    def _GetBufferCapacity(self: "GarbageCollectingPhyloTracker") -> int:
        return self._parentage_buffer.shape[0]

    def _MaybeGarbageCollect(
        self: "GarbageCollectingPhyloTracker", num_to_insert: int
    ) -> bool:

        if self._num_records + num_to_insert >= self._GetBufferCapacity():
            referenced_rows = _discern_referenced_rows(
                self._parentage_buffer,
                self._num_records,
                self._population_size,
            )
            num_referenced_rows = np.sum(referenced_rows)
            cumsum = np.cumsum(np.invert(referenced_rows))
            self._parentage_buffer[: self._num_records] -= cumsum[
                self._parentage_buffer[: self._num_records]
            ]

            # condense non-garbage-collected rows to front of buffer
            self._parentage_buffer[
                :num_referenced_rows
            ] = self._parentage_buffer[: self._num_records][referenced_rows]

            self._num_records = num_referenced_rows

            return True
        else:
            return False

    def _MaybeGrowBuffer(
        self: "GarbageCollectingPhyloTracker", num_to_insert: int
    ) -> None:
        while (
            self._num_records + num_to_insert
            >= 0.5 * self._GetBufferCapacity()
        ):
            self._parentage_buffer.resize(int(self._GetBufferCapacity() * 1.5))

    def ElapseGeneration(
        self: "GarbageCollectingPhyloTracker",
        parent_idxs: typing.List[int],
    ) -> None:

        assert self._population_size == len(parent_idxs)

        # if elements will overflow buffer, try garbage collecting
        if self._MaybeGarbageCollect(self._population_size):
            # if garbage collecting didn't make enough space, increase buffer
            # size
            self._MaybeGrowBuffer(self._population_size)

        assert self._num_records < self._GetBufferCapacity()
        assert (
            self._num_records + self._population_size
            < self._GetBufferCapacity()
        )

        begin_row = self._num_records
        end_row = begin_row + self._population_size
        self._parentage_buffer[begin_row:end_row] = (
            begin_row - self._population_size + parent_idxs
        )

        self._num_records = end_row

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
