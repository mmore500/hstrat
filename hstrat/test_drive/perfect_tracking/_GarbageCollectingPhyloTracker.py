import types
import typing

import numpy as np
import pandas as pd

from ..._auxiliary_lib import apply_swaps, count_unique
from ._GarbageCollectingPhyloTracker_ import _discern_referenced_rows


class GarbageCollectingPhyloTracker:

    _population_size: int
    _num_records: int
    _parentage_buffer: np.array  # [int]

    _loc_buffer: np.array  # [int]
    _trait_buffer: np.array  # [float]

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

    _working_buffer_size: int

    def __init__(
        self: "GarbageCollectingPhyloTracker",
        initial_population: typing.Union[int, np.array],  # [float]
        working_buffer_size: typing.Optional[int] = None,
        share_common_ancestor: bool = True,
    ) -> None:

        if isinstance(initial_population, int):
            initial_population = np.full(initial_population, np.nan)

        self._population_size = len(initial_population)
        assert self._population_size

        if working_buffer_size is None:
            working_buffer_size = 1000 * self._population_size

        self._working_buffer_size = working_buffer_size
        self._working_buffer_end = working_buffer_size

        assert (
            working_buffer_size
            >= self._population_size + share_common_ancestor
        )

        initial_buffer_size = working_buffer_size * 3 // 2
        self._parentage_buffer = np.empty(
            initial_buffer_size,
            dtype=np.int32,
        )
        self._loc_buffer = np.empty(
            initial_buffer_size,
            dtype=np.min_scalar_type(self._population_size),
        )
        self._trait_buffer = np.empty(
            initial_buffer_size,
            dtype=np.single,
        )

        self._num_records = self._population_size + share_common_ancestor

        if share_common_ancestor:
            self._parentage_buffer[0] = 0
            self._loc_buffer[0] = 0
            self._trait_buffer[0] = np.nan

            self._parentage_buffer[1 : self._population_size + 1] = 0
            self._loc_buffer[1 : self._population_size + 1] = np.arange(
                self._population_size
            )
            self._trait_buffer[
                1 : self._population_size + 1
            ] = initial_population
        else:
            self._parentage_buffer[: self._population_size] = np.arange(
                self._population_size
            )
            self._loc_buffer[: self._population_size] = np.arange(
                self._population_size
            )
            self._trait_buffer[: self._population_size] = initial_population

    def _GetBufferCapacity(self: "GarbageCollectingPhyloTracker") -> int:
        return self._parentage_buffer.shape[0]

    def _GarbageCollect(
        self: "GarbageCollectingPhyloTracker",
        below_row: int = 0,
    ) -> None:
        assert self._num_records > below_row

        referenced_rows = _discern_referenced_rows(
            self._parentage_buffer,
            self._num_records,
            self._population_size,
            below_row,
        )
        num_referenced_rows = np.sum(referenced_rows)
        cumsum = np.cumsum(np.invert(referenced_rows))
        targets = (
            self._parentage_buffer[below_row : self._num_records] - below_row
        )
        if below_row:
            adjustment = cumsum[np.maximum(targets, 0)]
            adjustment[targets < 0] = 0
        else:
            adjustment = cumsum[targets]
        self._parentage_buffer[below_row : self._num_records] -= adjustment

        # condense non-garbage-collected rows to front of buffer
        self._parentage_buffer[
            below_row : below_row + num_referenced_rows
        ] = self._parentage_buffer[below_row : self._num_records][
            referenced_rows
        ]
        self._trait_buffer[
            below_row : below_row + num_referenced_rows
        ] = self._trait_buffer[below_row : self._num_records][referenced_rows]
        self._loc_buffer[
            below_row : below_row + num_referenced_rows
        ] = self._loc_buffer[below_row : self._num_records][referenced_rows]

        self._num_records = num_referenced_rows + below_row

        self._working_buffer_end = (
            self._num_records + 2 * self._working_buffer_size // 3
        )

    def _GarbageCollectWorkingBuffer(
        self: "GarbageCollectingPhyloTracker",
    ) -> bool:
        self._GarbageCollect(
            max(self._num_records - self._working_buffer_size, 0)
        )

    def _WouldInsertionOverflow(
        self: "GarbageCollectingPhyloTracker", num_to_insert: int
    ) -> bool:
        return self._num_records + num_to_insert >= self._GetBufferCapacity()

    def _GrowBuffer(self: "GarbageCollectingPhyloTracker") -> None:
        # refcheck only seems to fail in coverage build,
        # but set False everywhere anyways
        self._parentage_buffer.resize(
            int(self._GetBufferCapacity() * 1.5),
            refcheck=False,
        )
        self._trait_buffer.resize(
            int(self._GetBufferCapacity() * 1.5),
            refcheck=False,
        )
        self._loc_buffer.resize(
            int(self._GetBufferCapacity() * 1.5),
            refcheck=False,
        )

    def _GrowBufferForInsertion(
        self: "GarbageCollectingPhyloTracker", num_to_insert: int
    ) -> None:
        while self._WouldInsertionOverflow(num_to_insert):
            self._GrowBuffer()

    def ElapseGeneration(
        self: "GarbageCollectingPhyloTracker",
        parent_locs: typing.List[int],
        traits: typing.Optional[typing.List[float]] = None,
    ) -> None:
        assert self._population_size == len(parent_locs)

        if self._num_records >= self._working_buffer_end:
            self._GarbageCollectWorkingBuffer()

        if self._WouldInsertionOverflow(self._population_size):
            self._GrowBufferForInsertion(self._population_size)
            self._GarbageCollect()

        begin_row = self._num_records
        end_row = begin_row + self._population_size
        self._parentage_buffer[begin_row:end_row] = (
            begin_row - self._population_size + parent_locs
        )
        self._loc_buffer[begin_row:end_row] = np.arange(self._population_size)
        if traits is not None:
            self._trait_buffer[begin_row:end_row] = traits

        self._num_records = end_row

    def ApplyLocSwaps(
        self: "GarbageCollectingPhyloTracker",
        swapfrom_locs: np.array,  # [int]
        swapto_locs: np.array,  # [int]
    ) -> None:
        begin_row = self._num_records - self._population_size
        end_row = self._num_records
        apply_swaps(
            self._parentage_buffer[begin_row:end_row],
            swapfrom_locs,
            swapto_locs,
        )
        apply_swaps(
            self._trait_buffer[begin_row:end_row], swapfrom_locs, swapto_locs
        )

    def ApplyLocPasteovers(
        self: "GarbageCollectingPhyloTracker",
        copyfrom_locs: np.array,  # [int]
        copyto_locs: np.array,  # [int]
    ) -> None:
        assert len(copyto_locs) == count_unique(copyto_locs)

        begin_row = self._num_records - self._population_size
        end_row = self._num_records
        self._parentage_buffer[begin_row:end_row][
            copyto_locs
        ] = self._parentage_buffer[begin_row:end_row][copyfrom_locs].copy()
        self._trait_buffer[begin_row:end_row][
            copyto_locs
        ] = self._trait_buffer[begin_row:end_row][copyfrom_locs].copy()

    def CompilePhylogeny(
        self: "GarbageCollectingPhyloTracker",
        progress_wrap=lambda x: x,
        loc_transforms: typing.Dict[
            str, typing.Callable
        ] = types.MappingProxyType({}),
    ) -> pd.DataFrame:

        self._GarbageCollect()
        records = [
            {
                **{
                    "id": idx,
                    "ancestor_list": str(
                        [parent_idx if parent_idx != idx else None]
                    ),
                    "loc": loc,
                    "trait": trait,
                },
                **{
                    key: transform(loc)
                    for key, transform in loc_transforms.items()
                },
            }
            for idx, (parent_idx, loc, trait) in enumerate(
                zip(
                    progress_wrap(self._parentage_buffer[: self._num_records]),
                    self._loc_buffer[: self._num_records],
                    self._trait_buffer[: self._num_records],
                )
            )
        ]
        return pd.DataFrame.from_records(records)
