import typing  # pragma: no cover

from deprecated.sphinx import deprecated  # pragma: no cover
import numpy as np  # pragma: no cover
import pandas as pd  # pragma: no cover

from ..._auxiliary_lib import indices_of_unique  # pragma: no cover
from ._compile_phylogeny_from_lineage_iters import (  # pragma: no cover
    compile_phylogeny_from_lineage_iters,
)


# @MAM 02-04-2023
# created a partial implementation of missing features before testing showed
# it underperformed the GC tracker; left partial implementation here:
# https://gist.github.com/mmore500/06a359e528f59f3feb0c72dfc01b8fef
@deprecated(
    version="1.13.0", reason="Incompatible with numpy v2"
)  # pragma: no cover
class DecantingPhyloTracker:  # pragma: no cover
    """Data structure to enable perfect tracking over a fixed-size population
    with synchronous generations.

    Generally less performant than GarbageCollectingPhyloGracker; represents
    organism records as independent objects (which each require an independent
    allocations and, on lineage extinction, deletions). Uses a decanting buffer
    to reduce object creation overhead by only allocating record objects for
    organisms that produce extant lineages beyond a threshold length.

    Does not include organism population loc and trait values in phylogenetic
    record.
    """

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
    #                     population loc of extant organisms
    #                     |
    #                     |
    # generations ago ----|-> 0   1   2   3   4   ...   buffer_size - 1
    # from extant         V +----------------------------------------
    # organisms           0 |
    #                     1 |         POPULATION
    #                     2 |          POSITION
    #                     3 |             IDS
    #                     4 |
    #                   ... |
    #   population_size - 1 |
    #
    # layer 0 (z axis): organism's own population loc
    # layer 1 (z axis): parent's population loc
    #
    # every generation,
    # * the backtrack tree is updated using the subset population loc ids'
    #   that survived to the rightmost colun,
    # * population loc ids roll one column to the right,
    # * new population loc id's are pasted over column 0,
    # * and rows shuffle/duplicate according to the selected parent indices
    #
    _decanting_buffer: np.ndarray  # [int]
    _buffer_pos: int  # current start position of circular decanting buffer

    # permanent phylogeny storage after consolidation traversing decant buffer
    # using tuples instead of PerfectBacktrackHandle gives significant speedup
    _decanted_tree_tips: np.ndarray  # [typing.Tuple]

    def __init__(
        self: "DecantingPhyloTracker",
        population_size: int,
        buffer_size: int = 10,
        share_common_ancestor: bool = True,
    ) -> None:
        """Initialize data structure to perfectly track phylogenetic history of
        a population.

        Parameters
        ----------
        population_size : int
            How many locations are available within the tracked fixed-size
            population?
        buffer_size : int, optional
            How many generations should lineages be decanted before creating
            record objects for organisms with extant lineages?
        share_common_ancestor : bool, default True
            Should a dummy common ancestor be inserted as the first entry in
            the tracker?

            If True, all initial population members will be recorded as
            children of this dummy ancestor. If False, all initial
            population members will be recorded as having no parent.
        """

        if np.lib.NumpyVersion(np.__version__) >= "2.0.0b1":
            raise ImportError("This module is not compatible with numpy v2.")

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
            # need to use mutable lists so ancestors have distinct id
            # because contents (i.e., None) are identical
            handles = [[None] for __ in range(population_size)]
            assert len(set(map(id, handles))) == len(handles)

        handles_array = np.empty(len(handles), dtype=object)
        handles_array[:] = handles
        self._decanted_tree_tips = handles_array
        assert len(set(map(id, self._decanted_tree_tips))) == len(handles)

    def _ArchiveBufferTail(
        self: "DecantingPhyloTracker",
    ):
        """Create record objects for decanted organisms with extant
        lineages."""
        assert not self._is_nan(self._decanting_buffer[0, self._buffer_pos, 0])

        # find locs of unique ancestors with extant descendants
        unique_row_indices = indices_of_unique(
            self._decanting_buffer[:, self._buffer_pos, 0],
        )

        unique_locs = self._decanting_buffer[
            unique_row_indices, self._buffer_pos, 0
        ]
        unique_parent_locs = self._decanting_buffer[
            unique_row_indices, self._buffer_pos, 1
        ]
        # apply unique ancestors' generational step
        # to relevant perfect tracking handles
        # step 1: copy parents
        self._decanted_tree_tips[unique_locs] = self._tuple_wrap(
            self._decanted_tree_tips[unique_parent_locs]
        )

    def _AdvanceBuffer(
        self: "DecantingPhyloTracker",
    ) -> None:
        """Progress circular decanting buffer, archiving buffer tail first if
        necessary."""
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
        parent_locs: typing.List[int],
    ) -> None:
        """Append generational turnover to the phylogenetic record.

        Parameters
        ----------
        parent_locs : array_like of int
            Parent's population loc for each population loc.

            Position within array corresponds to post-turnover population
            members' population positions. Values within array correspond to
            those members' parents' population positions within the pre-
            turnover population.
        """
        # consolidate rows that now share common ancestry
        self._decanting_buffer = self._decanting_buffer[parent_locs, :, :]

        # shift buffer one position right,
        # archiving rightmost column if necessary
        self._AdvanceBuffer()

        # set new (leftmost) column
        # note: 0 - 1 == -1 is valid for indexing
        # layer 0: own population loc
        self._decanting_buffer[:, self._buffer_pos - 1, 0] = np.arange(
            self._decanting_buffer.shape[0]
        )
        # layer 1: parent population loc
        self._decanting_buffer[:, self._buffer_pos - 1, 1] = parent_locs

    def _FlushBuffer(self: "DecantingPhyloTracker") -> None:
        """Clear decanting buffer, creating record objects for all organisms
        currently progressing through the decanting process."""
        # advance buffer and fill column 0 with nan until empty
        # note: buffer may only be partway full, in which case
        # columns will shift rightwards until reaching rightmost column
        # and then begin to be archived
        while not np.all(self._decanting_buffer.flatten(), self._nan_val):
            self._AdvanceBuffer()
            self._decanting_buffer[:, self._buffer_pos - 1, :] = self._nan_val

    def CompilePhylogeny(
        self: "DecantingPhyloTracker",
        progress_wrap=lambda x: x,
    ) -> pd.DataFrame:
        """Generate full phylogenetic record of extant organisms.

        Parameters
        ----------
        progress_wrap : Callable, optional
            Wrapper applied around record row iterator; pass tqdm or equivalent
            to display progress bar for compilation process.

        Returns
        -------
        pandas.DataFrame
            Full phylogenetic record of extant organisms alife standard format.

        Notes
        -----
        This operation is non-destructive; further record-keeping may be
        performed on the tracker object afterwards.
        """
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
            iter_lineage(tip)
            for tip in progress_wrap(self._decanted_tree_tips)
        )
