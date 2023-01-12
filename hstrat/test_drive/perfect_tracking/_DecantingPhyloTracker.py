import collections
import typing

import numpy as np
import pandas as pd

from ._PerfectBacktrackHandle import PerfectBacktrackHandle
from ._compile_perfect_backtrack_phylogeny import (
    compile_perfect_backtrack_phylogeny,
)
from ._iter_perfect_backtrack_lineage import iter_perfect_backtrack_lineage


class DecantingPhyloTracker:

    # static class constant
    _nan_val = -1

    @staticmethod
    def _is_nan(v: int) -> bool:
        return v < 0

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
    _decanting_buffer: np.array  # [int]

    # permanent phylogeny storage after consolidation traversing decant buffer
    _decanted_tree_tips: np.array  # [PerfectBacktrackHandle]

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

        if share_common_ancestor:
            common_ancestor = PerfectBacktrackHandle()
            self._decanted_tree_tips = np.array(
                [
                    common_ancestor.CreateDescendant()
                    for __ in range(population_size)
                ]
            )
        else:
            self._decanted_tree_tips = np.array(
                [PerfectBacktrackHandle() for __ in range(population_size)]
            )

    def _ArchiveBufferTail(
        self: "DecantingPhyloTracker",
    ):
        assert not self._is_nan(self._decanting_buffer[0, -1, 0])

        # find positions of unique ancestors with extant descendants
        __, unique_indices = np.unique(
            self._decanting_buffer[:, -1, 0],
            return_index=True,
        )

        # apply unique ancestors' generational step
        # to relevant perfect tracking handles
        # step 1: copy parents
        self._decanted_tree_tips[
            self._decanting_buffer[unique_indices, -1, 0]
        ] = self._decanted_tree_tips[
            self._decanting_buffer[unique_indices, -1, 1]
        ]
        # step 2: elapse generation
        for tip_idx in self._decanting_buffer[unique_indices, -1, 0]:
            self._decanted_tree_tips[tip_idx] = self._decanted_tree_tips[
                tip_idx
            ].CreateDescendant()

    def _AdvanceBuffer(
        self: "DecantingPhyloTracker",
    ) -> None:
        # if buffer is full empty, archive the oldest data before overwriting
        if not self._is_nan(self._decanting_buffer[0, -1, 0]):
            self._ArchiveBufferTail()

        # copy columns 0 thru buffer_size - 2 one column rightwards
        self._decanting_buffer[:, 1:, :] = self._decanting_buffer[:, :-1, :]

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
        # layer 0: own population position
        self._decanting_buffer[:, 0, 0] = np.arange(
            self._decanting_buffer.shape[0]
        )
        # layer 1: parent population position
        self._decanting_buffer[:, 0, 1] = parent_idxs

    def _FlushBuffer(self: "DecantingPhyloTracker") -> None:

        # advance buffer and fill column 0 with nan until empty
        # note: buffer may only be partway full, in which case
        # columns will shift rightwards until reaching rightmost column
        # and then begin to be archived
        while not np.all(self._decanting_buffer.flatten(), self._nan_val):
            self._AdvanceBuffer()
            self._decanting_buffer[:, 0, :] = self._nan_val

    def CompilePhylogeny(self: "DecantingPhyloTracker") -> pd.DataFrame:
        self._FlushBuffer()
        assert set(self._decanting_buffer.flatten()) == {self._nan_val}
        return compile_perfect_backtrack_phylogeny(self._decanted_tree_tips)
