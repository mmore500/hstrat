import collections
import typing

import numpy as np
import pandas as pd

from ..._auxiliary_lib import indices_of_unique
from ._compile_phylogeny_from_lineage_iters import (
    compile_phylogeny_from_lineage_iters,
)


class DecantingPhyloTracker:

    # static class constant
    _nan_val = -1

    @staticmethod
    def _is_nan(v: int) -> bool:
        return v < 0

    @staticmethod
    @np.vectorize
    def _tuple_wrap(v: typing.Any) -> typing.Tuple:
        return (v,)

    # decanting buffer layout
    #
    #                     population position
    #                     |
    #                     |
    # generations ago ----|-> 0   1   2   3   4   ...   buffer_size - 1
    #                     V +----------------------------------------
    #                     0 |
    #                     1 |         POPULATION
    #                     2 |          POSITION
    #                     3 |             IDS
    #                     4 |
    #                   ... |
    #   population_size - 1 |
    #
    # layer 0 (z axis): own population position
    # layer 1 (z axis): parent's population position
    #
    # every generation,
    # * the backtrack tree is updated using the subset population position ids' #   that survived to the rightmost colun,
    # * population position ids roll one column to the right,
    # * new population position id's are pasted over column 0,
    # * and rows shuffle/duplicate according to the selected parent indexes
    #
    _buffer_pos: int
    _decanting_buffer: np.array  # [int]

    # permanent phylogeny storage after consolidation traversing decant buffer
    # using tuples instead of PerfectBacktrackHandle gives significant speedup
    _decanted_tree_tips: np.array  # [typing.Tuple]

    def __init__(
        self: "DecantingPhyloTracker",
        population_size: int,
        buffer_size: int = 10,
        share_common_ancestor: bool = True,
    ) -> None:
        """Create backtracking breadcrumb, with `parent` as preceding
        breadcrumb in line of descent or `None` if associated with seed
        organism."""

        # initialize decanting buffer with all nan values
        self._decanting_buffer = np.full(
            (population_size, buffer_size, 2),
            self._nan_val,
            dtype=np.min_scalar_type(-population_size + 1),
        )
        self._buffer_pos = 0

        handles = []
        if share_common_ancestor:
            common_ancestor = (None,)
            # can't use list comprehension due to non-distinct tuple ids
            handles = []
            for __ in range(population_size):
                handle = (common_ancestor,)
                handles.append(handle)
            assert len(set(map(id, handles))) == len(handles)
            assert len(set(map(lambda x: id(x[0]), handles))) == 1
        else:
            # can't use list comprehension due to non-distinct tuple ids
            for __ in range(population_size):
                handle = (None,)
                handles.append(handle)
            assert len(set(map(id, handles))) == len(handles)

        handles_array = np.empty(len(handles), dtype=object)
        handles_array[:] = handles
        self._decanted_tree_tips = handles_array
        assert len(set(map(id, self._decanted_tree_tips))) == len(handles)

    def _ArchiveBufferTail(
        self: "DecantingPhyloTracker",
    ):
        assert not self._is_nan(self._decanting_buffer[0, self._buffer_pos, 0])

        # find positions of unique ancestors with extant descendants
        unique_row_indices = indices_of_unique(
            self._decanting_buffer[:, self._buffer_pos, 0],
        )

        unique_positions = self._decanting_buffer[
            unique_row_indices, self._buffer_pos, 0
        ]
        unique_parent_positions = self._decanting_buffer[
            unique_row_indices, self._buffer_pos, 1
        ]
        # apply unique ancestors' generational step
        # to relevant perfect tracking handles
        # step 1: copy parents
        self._decanted_tree_tips[unique_positions] = self._tuple_wrap(
            self._decanted_tree_tips[unique_parent_positions]
        )

    def _AdvanceBuffer(
        self: "DecantingPhyloTracker",
    ) -> None:
        # if rightmost column not empty, archive it before overwriting
        if not self._is_nan(self._decanting_buffer[0, self._buffer_pos, 0]):
            self._ArchiveBufferTail()

        # copy columns 0 thru buffer_size - 2 one column rightwards
        self._buffer_pos += 1
        # wrap buffer position around
        self._buffer_pos -= self._decanting_buffer.shape[1] * (
            self._buffer_pos >= self._decanting_buffer.shape[1]
        )

    def ElapseGeneration(
        self: "DecantingPhyloTracker",
        parent_idxs: typing.List[int],
    ) -> None:

        # consolidate rows that now share common ancestry
        self._decanting_buffer = self._decanting_buffer[parent_idxs, :, :]

        # shift buffer one position right,
        # archiving rightmost column if necessary
        self._AdvanceBuffer()

        # set new (leftmost) column
        # note: 0 - 1 == -1 is valid for indexing
        # layer 0: own population position
        self._decanting_buffer[:, self._buffer_pos - 1, 0] = np.arange(
            self._decanting_buffer.shape[0]
        )
        # layer 1: parent population position
        self._decanting_buffer[:, self._buffer_pos - 1, 1] = parent_idxs


    def _FlushBuffer(self: "DecantingPhyloTracker") -> None:

        # advance buffer and fill column 0 with nan until empty
        # note: buffer may only be partway full, in which case
        # columns will shift rightwards until reaching rightmost column
        # and then begin to be archived
        while not np.all(self._decanting_buffer.flatten(), self._nan_val):
            self._AdvanceBuffer()
            self._decanting_buffer[:, self._buffer_pos - 1, :] = self._nan_val

    def CompilePhylogeny(self: "DecantingPhyloTracker") -> pd.DataFrame:
        self._FlushBuffer()
        assert set(self._decanting_buffer.flatten()) == {self._nan_val}

        def iter_lineage(
            tuple_handle: typing.Tuple,
        ) -> typing.Iterable[typing.Tuple]:
            while True:
                yield tuple_handle

                if tuple_handle[0] is None:
                    break
                else:
                    tuple_handle = tuple_handle[0]

        return compile_phylogeny_from_lineage_iters(
            iter_lineage(tip) for tip in self._decanted_tree_tips
        )
