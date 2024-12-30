import collections
import types
import typing

import numpy as np
import pandas as pd

from ..._auxiliary_lib import apply_swaps, count_unique
from ._GarbageCollectingPhyloTracker_ import _discern_referenced_rows


class GarbageCollectingPhyloTracker:
    """Data structure to enable perfect tracking over a fixed-size population
    with synchronous generations.

    Designed to provide low-overhead tracking. Instead of representing organism
    records as independent objects (which each require an independent
    allocations and, on lineage extinction, deletions), stores organism records
    as rows within a numpy array. Partial garbage collection at regular
    intervals compacts recent record entries to discard extinct lineages.

    Includes organism population loc and trait values in phylogenetic record.
    """

    _population_size: int
    _working_buffer_size: int

    _parentage_buffer: np.ndarray  # [int]
    """1d array with entries representing individual organisms and stored
    value at each entry corresponding to index of entry representing that
    organism's parent."""

    _num_records: int
    """How many entries are stored in `_parentage_buffer`? May be less than
    `len(_parentage_buffer)`."""

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

    _loc_buffer: np.ndarray  # [int]
    """Population position of each tracked organism; entries describe same
    organism as entry with corresponding row index in `_parentage_buffer`."""

    _trait_buffer: np.ndarray  # [float]
    """Phenotypic trait of each tracked organism; entries describe same
    organism as entry with corresponding row index in `_parentage_buffer`."""

    def __init__(
        self: "GarbageCollectingPhyloTracker",
        initial_population: typing.Union[int, np.ndarray],  # [float]
        working_buffer_size: typing.Optional[int] = None,
        share_common_ancestor: bool = True,
    ) -> None:
        """Initialize data structure to perfectly track phylogenetic history of
        a population.

        Parameters
        ----------
        initial_population : int or numpy array of float
            Specification of founding organisms of population. Providing an
            integer argument specifices population size, and founding organisms'
            float phenotypic traits are recorded as NaN. Providing a numpy
            array of float specifies phenotypic traits of founding organisms.
        working_buffer_size : int, optional
            Intermittent garbage collection depth.

            How many rows back should intermittent garbage collection reach?
            Adjustments to this parameter only affect performance, not tracking
            semantics. Initial buffer size is set to 150% of
            `working_buffer_size`.
        share_common_ancestor : bool, default True
            Should a dummy common ancestor be inserted as the first entry in
            the tracker?

            If True, all initial population members will be recorded as
            children of this dummy ancestor. If False, all initial
            population members will be recorded as having no parent.

            The dummy ancestor's trait value is recorded as NaN and population
            loc is recorded as 0.
        """

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
        """How much buffer space is allocated?"""
        return self._parentage_buffer.shape[0]

    def _GarbageCollect(
        self: "GarbageCollectingPhyloTracker",
        below_row: int = 0,
    ) -> None:
        """Prune entries with extinct lineages at or after `below_row`."""
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
        """Prune entries with extinct lineages within the fixed-size working
        buffer segment."""
        self._GarbageCollect(
            max(self._num_records - self._working_buffer_size, 0)
        )

    def _WouldInsertionOverflow(
        self: "GarbageCollectingPhyloTracker", num_to_insert: int
    ) -> bool:
        """Is buffer capacity sufficinet to accomodate `num_to_insert`
        insertions?"""
        return self._num_records + num_to_insert >= self._GetBufferCapacity()

    def _GrowBuffer(self: "GarbageCollectingPhyloTracker") -> None:
        """Allocate a additional buffer space.

        Buffer grows by a fixed proportion of current buffer size.
        """
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
        """Allocate sufficient additional buffer space to accommodate
        `num_to_insert` insertions."""
        while self._WouldInsertionOverflow(num_to_insert):
            self._GrowBuffer()

    def ElapseGeneration(
        self: "GarbageCollectingPhyloTracker",
        parent_locs: typing.List[int],  # np.ndarray ok
        traits: typing.Optional[typing.List[float]] = None,  # np.ndarray ok
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
        traits: array_like of float, optional
            Traits of post-turnover population members.

            If unspecified, post-turnover population members' traits are
            recorded as NaN.
        """
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
        swapfrom_locs: np.ndarray,  # [int]
        swapto_locs: np.ndarray,  # [int]
    ) -> None:
        """Swap organisms between population locations.

        Organisms' pre-swap population locations do not remain in the
        phylogenetic record. Zip of parameters specifies pairs of population
        locations to swap.

        Notes
        -----
        Swaps are performed sequentially, with the most recent organism swapped
        to a location used for subsequent swaps from or to that location.

        Parameter order is commutative.
        """
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
        copyfrom_locs: np.ndarray,  # [int]
        copyto_locs: np.ndarray,  # [int]
    ) -> None:
        """Replace organisms at `copyto_locs` locations with non-descendant
        clones of organisms at `copyfrom_locs` locations.

        Pasted-over organisms do not remain in the phylogenetic record. The
        pasted-in organism is not recorded as the child of the pasted-from
        organism; rather, the pasted-in organism is recorded as the child of
        the pasted-from organism's parent.

        Zip of parameters specifies pasteovers to perform, with the first
        element of zipped tuples specifying the population location to copy
        from and the second element specifying the population location to paste
        over.

        Notes
        -----
        The original organism at each location is copied from, ignoring any
        preceding pasteovers that may have placed a new organism at that
        location during this operation.

        No repeated entries are allowed in `copyto_locs`.
        """
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
        """Generate full phylogenetic record of extant organisms.

        Parameters
        ----------
        progress_wrap : Callable, optional
            Wrapper applied around record row iterator; pass tqdm or equivalent
            to display progress bar for compilation process.
        loc_transforms: Dict of str -> Callable, default empty
            Specification for custom columns in returned dataframe.

            Each dict item creates a new column with name corresponding to the
            item's key populated with the result of mapping the item's Callable value over organisms' locs.

        Returns
        -------
        pandas.DataFrame
            Full phylogenetic record of extant organisms alife standard format.

        Notes
        -----
        This operation is non-destructive; further record-keeping may be
        performed on the tracker object afterwards.
        """
        self._GarbageCollect()
        generation_lookup = collections.Counter()

        records = []
        for idx, (parent_idx, loc, trait) in enumerate(
            zip(
                progress_wrap(self._parentage_buffer[: self._num_records]),
                self._loc_buffer[: self._num_records],
                self._trait_buffer[: self._num_records],
            )
        ):
            generation_lookup[idx] = generation_lookup[parent_idx] + (
                parent_idx != idx
            )
            records.append(
                {
                    **{
                        "id": idx,
                        "ancestor_list": str(
                            [int(parent_idx) if parent_idx != idx else None]
                        ),
                        "loc": loc,
                        "trait": trait,
                        "origin_time": generation_lookup[idx],
                    },
                    **{
                        key: transform(loc)
                        for key, transform in loc_transforms.items()
                    },
                }
            )
        return pd.DataFrame.from_records(records)
