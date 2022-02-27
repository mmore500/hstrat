from copy import copy
from interval_search import binary_search
from iterpop import iterpop as ip
import itertools as it
import math
import operator
import opytional as opyt
import typing

from .HereditaryStratum import HereditaryStratum
from .HereditaryStratumOrderedStoreList import HereditaryStratumOrderedStoreList

from .stratum_retention_condemners import StratumRetentionCondemnerFromPredicate
from .stratum_retention_condemners \
    import StratumRetentionCondemnerPerfectResolution


class HereditaryStratigraphicColumn:
    """Genetic annotation to enable phylogenetic inference among distributed
    digital evolution populations.

    Primary end-user facing interface for hstrat library. Should be bundled with
    digital genomes and propagated via the CloneDescendant method when passing
    those genomes from parent to offspring.

    Naming conventions are derived by analogy to Geological "Stratigraphy"
    (i.e., <https://en.wikipedia.org/wiki/Stratigraphy>). The "hereditary
    stratigraphy" system provided by this software works by associating an
    identifier, referred to as a "stratum," with each elapsed generation along
    a line of descent. This allows two "columns" to be aligned to detect the
    generation of their most recent common ancestor: strata before the MRCA
    will be identical and strata after will differ.

    Stratum retention policy and stratum differentia bit width can be configured
    to tune the time and space complexity of the column, trading-off with
    uncertainty induced on estimates of phylogenetic distance back to the most
    common recent ancestor of two columns.

    Arbitrary user-defined data can be associated with strata by optional
    argument to the CloneDescendant method. (Note that a first stratum is
    deposited during column initialization, so an optional annotation argument
    may also be provided then.)
    """

    # if True, strata will be constructed with deposition rank stored even if
    # the stratum retention condemner does not require it
    _always_store_rank_in_stratum: bool
    # how many bits wide of differentia should the deposted strata be
    # constructed with?
    _stratum_differentia_bit_width: int
    # counter tracking the number of strata deposited
    # incremented *after* a deposition and its coinciding purge are complete
    _num_strata_deposited: int
    # data structure storing retained strata
    _stratum_ordered_store: typing.Any
    # functor specifying stratum retention policy
    _stratum_retention_condemner: typing.Callable

    def __init__(
        self: 'HereditaryStratigraphicColumn',
        *,
        always_store_rank_in_stratum: bool=True,
        stratum_differentia_bit_width: int=64,
        initial_stratum_annotation: typing.Optional[typing.Any]=None,
        stratum_retention_condemner: typing.Callable=None,
        stratum_retention_predicate: typing.Callable=None,
        stratum_ordered_store_factory: typing.Callable
            =HereditaryStratumOrderedStoreList,
    ):
        """Initialize column to track a new line of descent.

        Deposits a first stratum, so GetNumStrataDeposited() will return 1 after
        initialization even though the user has not yet called DepositStratum().

        Parameters
        ----------
        always_store_rank_in_stratum : bool, optional
            Should the deposition rank be stored as a data member of generated
            strata, even if not strictly necessary?
        stratum_differentia_bit_width : int, optional
            The bit width of the generated differentia. Default 64, allowing
            for 2^64 distinct values.
        initial_stratum_annotation: any, optional
            Optional object to store as an annotation. Allows arbitrary user-
            provided to be associated with the first stratum deposition in the
            line of descent.
        stratum_retention_condemner : callable, optional
            Functor that implements stratum retention policy by specifying
            the set of strata ranks that should be pruned from a hereditary
            stratigraphic column when the nth stratum is deposited. Mutually
            exclusive with stratum_retention_predicate; only one should be
            specified.
        stratum_retention_predicate : callable, optional
            Functor that implements stratum retention policy by specifying
            whether a stratum with deposition rank r should be retained within
            a hereditary stratigraphic column after n strata have been
            deposited. Mutually exclusive with stratum_retention_condemner;
            only one should be specified.
        stratum_ordered_store_factory : callable, optional
            Callable to generate a container that implements the necessary
            interface to store strata within the column. Can be configured for
            performance reasons, but has no semantic effect. A type that can be
            default-constructed will suffice.

        Notes
        -----
        If no condemner or predicate functor specifying a stratum retention
        policy is provided, the perfect resolution policy where all strata are
        retained is used.
        """
        self._always_store_rank_in_stratum = always_store_rank_in_stratum
        self._stratum_differentia_bit_width = stratum_differentia_bit_width
        self._num_strata_deposited = 0
        self._stratum_ordered_store = stratum_ordered_store_factory()

        if None not in (
            stratum_retention_predicate,
            stratum_retention_condemner,
        ):
            raise ValueError(
                'Exactly one of `stratum_retention_condemner` '
                'and `stratum_retention_predicate` must be provided.'
            )
        else:
            self._stratum_retention_condemner = (
                StratumRetentionCondemnerFromPredicate(
                    stratum_retention_predicate,
                )
                    if (stratum_retention_predicate is not None)
                else stratum_retention_condemner
                    if stratum_retention_condemner is not None
                else StratumRetentionCondemnerPerfectResolution()
            )

        self.DepositStratum(annotation=initial_stratum_annotation)

    def __eq__(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> bool:
        """Compare for value-wise equality."""

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def _ShouldOmitStratumDepositionRank(
        self: 'HereditaryStratigraphicColumn',
    ) -> bool:
        """Implementation detail to inspect configured stratum retention policy
        and manual override to decide whether deposition rank should be stored
        as a data member of generated strata.

        Note that strata are not required to be stored if the stratum retention
        policy allows for the rank of a stratum to be calcualted as a function
        of its position within the column and the number of strata deposited
        onto the column. However, it may be beneficial to store the stratum
        anyways for performance reasons if this calculation is expenxive.
        """

        can_omit_deposition_rank = hasattr(
            self._stratum_retention_condemner,
            'CalcRankAtColumnIndex',
        )
        return (
            can_omit_deposition_rank
            and not self._always_store_rank_in_stratum
        )

    def DepositStratum(
        self: 'HereditaryStratigraphicColumn',
        annotation: typing.Optional[typing.Any]=None,
    ) -> None:
        """Elapse a generation.

        Parameters
        ----------
        annotation: any, optional
            Optional object to store as an annotation. Allows arbitrary user-
            provided to be associated with this stratum deposition in the
            line of descent.
        """

        new_stratum = HereditaryStratum(
            annotation=annotation,
            deposition_rank=(
                # don't store deposition rank if we know how to calcualte it
                # from stratum's position in column
                None
                if self._ShouldOmitStratumDepositionRank()
                else self._num_strata_deposited
            ),
            differentia_bit_width=self._stratum_differentia_bit_width,
        )
        self._stratum_ordered_store.DepositStratum(
            rank=self._num_strata_deposited,
            stratum=new_stratum,
        )
        self._PurgeColumn()
        self._num_strata_deposited += 1

    def _PurgeColumn(self: 'HereditaryStratigraphicColumn') -> None:
        """Implementation detail to discard stored strata according to the
        configured stratum retention policy.

        Called after a new stratum has been appended to the column's store but
        before it is considered fully deposited (i.e., it is reflected in the
        column's internal deposition counter).
        """

        condemned_ranks = self._stratum_retention_condemner(
            retained_ranks=self.GetRetainedRanks(),
            num_stratum_depositions_completed=self.GetNumStrataDeposited(),
        )
        self._stratum_ordered_store.DelRanks(
            ranks=condemned_ranks,
            get_column_index_of_rank=self.GetColumnIndexOfRank,
        )

    def GetRetainedRanks(
        self: 'HereditaryStratigraphicColumn',
    ) -> typing.Iterator[int]:
        """Get an iterator over deposition ranks of strata stored in the column.

        Order of iteration should not be considered guaranteed. The store may
        be altered during iteration without iterator invalidation, although
        subsequent updates will not be reflected in the iterator.
        """

        if self._ShouldOmitStratumDepositionRank():
            for idx in range(self.GetNumStrataRetained()):
                yield self.GetRankAtColumnIndex(idx)
        else:
            yield from self._stratum_ordered_store.GetRetainedRanks()

    def GetNumStrataRetained(self: 'HereditaryStratigraphicColumn') -> int:
        """How many strata are currently stored within the column?

        May be fewer than the number of strata deposited if strata have been
        discarded as part of the configured stratum retention policy.
        """

        return self._stratum_ordered_store.GetNumStrataRetained()

    def GetNumStrataDeposited(self: 'HereditaryStratigraphicColumn') -> int:
        """How many strata have been depostited on the column?

        Note that a first stratum is deposited on the column during
        initialization."""

        return self._num_strata_deposited

    def GetStratumAtColumnIndex(
        self: 'HereditaryStratigraphicColumn',
        index: int,
    ) -> HereditaryStratum:
        """Get the stratum positioned at index i among retained strata.

        Index order is from most ancient (index 0) to most recent.
        """

        return self._stratum_ordered_store.GetStratumAtColumnIndex(
            index,
            get_rank_at_column_index=(
                self.GetRankAtColumnIndex
                if self._ShouldOmitStratumDepositionRank()
                else None
            ),
        )

    def GetRankAtColumnIndex(
        self: 'HereditaryStratigraphicColumn',
        index: int,
    ) -> int:
        """What is the deposition rank of the stratum positioned at index i
        among retained strata?

        Index order is from most ancient (index 0) to most recent.
        """

        if self._ShouldOmitStratumDepositionRank():
            return self._stratum_retention_condemner.CalcRankAtColumnIndex(
                index=index,
                num_strata_deposited=self.GetNumStrataDeposited(),
            )
        else:
            # fall back to store lookup
            return self._stratum_ordered_store.GetRankAtColumnIndex(index)

    def GetColumnIndexOfRank(
        self: 'HereditaryStratumOrderedStoreList',
        rank: int,
    ) -> typing.Optional[int]:
        """What is the index position within retained strata of the stratum
        deposited at rank r?

        Returns None if no stratum with rank r is present within the store.
        """

        if self._ShouldOmitStratumDepositionRank():
            assert self.GetNumStrataRetained()
            res_idx = binary_search(
                lambda idx: self.GetRankAtColumnIndex(idx) >= rank,
                0,
                self.GetNumStrataRetained() - 1,
            )
            if res_idx is None:
                return None
            elif self.GetRankAtColumnIndex(res_idx) == rank:
                return res_idx
            else:
                return None
        else:
            # fall back to store lookup
            return self._stratum_ordered_store.GetColumnIndexOfRank(rank=rank)

    def GetNumDiscardedStrata(
        self: 'HereditaryStratigraphicColumn',
    ) -> int:
        """How many strata have been discarded by the configured column
        retention policy?"""

        return self.GetNumStrataDeposited() - self.GetNumStrataRetained()

    def HasDiscardedStrata(
        self: 'HereditaryStratigraphicColumn',
    ) -> bool:
        """Have any strata have been discarded by the configured column
        retention policy?"""

        return self.GetNumDiscardedStrata() > 0

    def CalcRankOfLastCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        """How many depositions elapsed along the columns' lines of
        descent before the last matching strata at the same rank between
        self and other?

        Returns
        -------
        int, optional
            The number of depositions elapsed or None if no common ancestor is
            shared between the columns.
        """

        if (
            self.HasDiscardedStrata()
            or other.HasDiscardedStrata()
            # for performance reasons
            # only binary search stores that support random access
            or not isinstance(
                self._stratum_ordered_store,
                HereditaryStratumOrderedStoreList
            )
            or not isinstance(
                other._stratum_ordered_store,
                HereditaryStratumOrderedStoreList
            )
        ):
            return self._do_generic_CalcRankOfLastCommonalityWith(other)
        else:
            return self._do_binary_search_CalcRankOfLastCommonalityWith(other)

    def _do_binary_search_CalcRankOfLastCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        """Implementation detail with optimized implementation for specialized
        case where both self and other use the perfect resolution stratum
        retention policy."""

        # both must have (effectively) used the perfect resolution policy
        assert not self.HasDiscardedStrata() and not other.HasDiscardedStrata()

        lower_bound = 0
        upper_bound = min([
            self.GetNumStrataDeposited() - 1,
            other.GetNumStrataDeposited() - 1,
        ])
        assert lower_bound <= upper_bound
        rank_at = lambda which, idx: which.GetRankAtColumnIndex(idx)
        differentia_at = lambda which, idx: \
                which.GetStratumAtColumnIndex(idx).GetDifferentia()
        predicate = lambda idx: \
            differentia_at(self, idx) != differentia_at(other, idx)

        first_disparite_idx = binary_search(
            predicate,
            lower_bound,
            upper_bound,
        )

        if first_disparite_idx is None:
            # no disparate strata found
            # fall back to _do_generic_CalcRankOfLastCommonalityWith to handle
            # proper bookkeeping in this case while skipping most of the search
            return self._do_generic_CalcRankOfLastCommonalityWith(
                other,
                self_start_idx=upper_bound,
                other_start_idx=upper_bound,
            )
        elif first_disparite_idx > 0:
            # disparate strata found, following some common strata
            last_common_idx = first_disparite_idx - 1
            last_common_rank = self.GetRankAtColumnIndex(
                last_common_idx,
            )
            return last_common_rank
        else:
            # no common strata between self and other
            return None

    def _do_generic_CalcRankOfLastCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        *,
        self_start_idx: int=0,
        other_start_idx: int=0,
    ) -> typing.Optional[int]:
        """Implementation detail with general-case implementation."""

        # helper setup
        self_iter = self._stratum_ordered_store.IterRankDifferentia(
            get_rank_at_column_index=self.GetRankAtColumnIndex,
            start_column_index=self_start_idx,
        )
        other_iter = other._stratum_ordered_store.IterRankDifferentia(
            get_rank_at_column_index=other.GetRankAtColumnIndex,
            start_column_index=other_start_idx,
        )
        self_cur_rank, self_cur_differentia = next(self_iter)
        other_cur_rank, other_cur_differentia = next(other_iter)

        last_common_rank = None
        # a.k.a.
        # while (
        #     self_column_idx < self.GetNumStrataRetained()
        #     and other_column_idx < other.GetNumStrataRetained()
        # ):
        try:
            while True:
                if (self_cur_rank == other_cur_rank):
                    # strata at same rank can be compared
                    if (self_cur_differentia == other_cur_differentia):
                        # matching differentiae at the same rank,
                        # store rank and keep searching for mismatch
                        last_common_rank = self_cur_rank
                        # advance self
                        self_cur_rank, self_cur_differentia = next(self_iter)
                        # advance other
                        other_cur_rank, other_cur_differentia = next(other_iter)
                    else:
                        # mismatching differentiae at the same rank
                        # a.k.a. break
                        raise StopIteration
                elif self_cur_rank < other_cur_rank:
                    # current stratum on self column older than on other column
                    # advance to next-newer stratum on self column
                    self_cur_rank, self_cur_differentia = next(self_iter)
                elif self_cur_rank > other_cur_rank:
                    # current stratum on other column older than on self column
                    # advance to next-newer stratum on other column
                    other_cur_rank, other_cur_differentia = next(other_iter)
        except StopIteration:
            return last_common_rank

    def CalcRankOfFirstDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        """How many depositions elapsed along the columns' lines of
        descent before the first mismatching strata at the same rank between
        self and other?

        Returns
        -------
        int, optional
            The number of depositions elapsed or None if no disparity (i.e.,
            both columns have same number of strata deposited and the most
            recent stratum is common between self and other).

        Notes
        -----
        If no mismatching strata are found but self and other have different
        numbers of strata deposited, this method returns one greater than the
        lesser of the columns' deposition counts.
        """

        if (
            self.HasDiscardedStrata()
            or other.HasDiscardedStrata()
            # for performance reasons
            # only apply binary search to stores that support random access
            or not isinstance(
                self._stratum_ordered_store,
                HereditaryStratumOrderedStoreList
            )
            or not isinstance(
                other._stratum_ordered_store,
                HereditaryStratumOrderedStoreList
            )
        ):
            return self._do_generic_CalcRankOfFirstDisparityWith(other)
        else:
            return self._do_binary_search_CalcRankOfFirstDisparityWith(other)

    def _do_binary_search_CalcRankOfFirstDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        """Implementation detail with optimized implementation for specialized
        case where both self and other use the perfect resolution stratum
        retention policy."""

        # both must have (effectively) used the perfect resolution policy
        assert not self.HasDiscardedStrata() and not other.HasDiscardedStrata()

        lower_bound = 0
        upper_bound = min([
            self.GetNumStrataDeposited() - 1,
            other.GetNumStrataDeposited() - 1,
        ])
        assert lower_bound <= upper_bound
        rank_at = lambda which, idx: which.GetRankAtColumnIndex(idx)
        differentia_at = lambda which, idx: \
                which.GetStratumAtColumnIndex(idx).GetDifferentia()
        predicate = lambda idx: \
            differentia_at(self, idx) != differentia_at(other, idx)

        first_disparite_idx = binary_search(
            predicate,
            lower_bound,
            upper_bound,
        )

        if first_disparite_idx is not None:
            # disparate strata found
            first_disparite_rank = self.GetRankAtColumnIndex(
                first_disparite_idx,
            )
            return first_disparite_rank
        else:
            # no disparate strata found
            # fall back to _do_generic_CalcRankOfFirstDisparityWith to handle
            # proper bookkeeping in this case while skipping most of the search
            return self._do_generic_CalcRankOfFirstDisparityWith(
                other,
                self_start_idx=upper_bound,
                other_start_idx=upper_bound,
            )

    def _do_generic_CalcRankOfFirstDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        *,
        self_start_idx: int=0,
        other_start_idx: int=0,
    ) -> typing.Optional[int]:
        """Implementation detail with general-case implementation."""

        # helper setup
        self_iter = self._stratum_ordered_store.IterRankDifferentia(
            get_rank_at_column_index=self.GetRankAtColumnIndex,
            start_column_index=self_start_idx,
        )
        other_iter = other._stratum_ordered_store.IterRankDifferentia(
            get_rank_at_column_index=other.GetRankAtColumnIndex,
            start_column_index=other_start_idx,
        )
        self_cur_rank, self_cur_differentia = next(self_iter)
        other_cur_rank, other_cur_differentia = next(other_iter)
        self_prev_rank: int
        other_prev_rank: int

        def advance_self():
            nonlocal self_prev_rank, self_cur_rank, \
                self_cur_differentia, self_iter
            try:
                self_prev_rank = self_cur_rank
                self_cur_rank, self_cur_differentia = next(self_iter)
            except StopIteration:
                self_iter = None

        def advance_other():
            nonlocal other_prev_rank, other_cur_rank, \
                other_cur_differentia, other_iter
            try:
                other_prev_rank = other_cur_rank
                other_cur_rank, other_cur_differentia = next(other_iter)
            except StopIteration:
                other_iter = None

        # a.k.a.
        # while (
        #     self_column_idx < self.GetNumStrataRetained()
        #     and other_column_idx < other.GetNumStrataRetained()
        # ):
        while self_iter is not None and other_iter is not None:
            if self_cur_rank == other_cur_rank:
                # strata at same rank can be compared
                if self_cur_differentia == other_cur_differentia:
                    # matching differentiae at the same rank,
                    # keep searching for mismatch
                    # advance self and other
                    # must ensure both advance, even if one stops iteration
                    advance_self()
                    advance_other()
                else:
                    # mismatching differentiae at the same rank
                    assert 0 <= self_cur_rank < self.GetNumStrataDeposited()
                    return self_cur_rank
            elif self_cur_rank < other_cur_rank:
                # current stratum on self column older than on other column
                # advance to next-newer stratum on self column
                advance_self()
            elif self_cur_rank > other_cur_rank:
                # current stratum on other column older than on self column
                # advance to next-newer stratum on other column
                advance_other()

        if self_iter is not None:
            # although no mismatching strata found between self and other
            # self has strata ranks beyond the newest found in other
            # conservatively assume mismatch will be with next rank of other
            assert other_iter is None
            res = other_prev_rank + 1
            assert 0 <= res <= self.GetNumStrataDeposited()
            assert 0 <= res <= other.GetNumStrataDeposited()
            return res
        elif other_iter is not None:
            # although no mismatching strata found between other and self
            # other has strata ranks beyond the newest found in self
            # conservatively assume mismatch will be with next rank
            assert self_iter is None
            res = self_prev_rank + 1
            assert 0 <= res <= self.GetNumStrataDeposited()
            assert 0 <= res <= other.GetNumStrataDeposited()
            return res
        else:
            # no disparate strata found
            # and self and other have the same newest rank
            assert self_iter is None and other_iter is None
            return None

    def CalcRankOfMrcaBoundsWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[typing.Tuple[int, int]]:
        """Calculate bounds on estimate for the number of depositions elapsed
        along the line of descent before the most recent common ancestor with
        other.

        Returns
        -------
        (int, int), optional
            Inclusive lower and then exclusive upper bound on estimate or None
            if no common ancestor is shared between self and other.

        See Also
        --------
        CalcRankOfMrcaUncertaintyWith :
            Wrapper to report uncertainty of calculated bounds.
        """

        if self.HasAnyCommonAncestorWith(other):
            first_disparity = self.CalcRankOfFirstDisparityWith(other)
            if first_disparity is None:
                num_self_deposited = self.GetNumStrataDeposited()
                num_other_deposited = other.GetNumStrataDeposited()
                assert num_self_deposited == num_other_deposited
            return (
                self.CalcRankOfLastCommonalityWith(other),
                opyt.or_value(first_disparity, self.GetNumStrataDeposited()),
            )
        else: return None

    def CalcRankOfMrcaUncertaintyWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> int:
        """Calculate uncertainty of estimate for the number of depositions
        elapsed along the line of descent before the most common recent
        ancestor with other.

        Returns 0 if no common ancestor is shared between self and other.

        See Also
        --------
        CalcRankOfMrcaBoundsWith :
            Calculates bound whose uncertainty this method reports. See the
            corresponding docstring for explanation of parameters.
        """

        bounds = self.CalcRankOfMrcaBoundsWith(other)
        return 0 if bounds is None else abs(operator.sub(*bounds)) - 1

    def CalcRanksSinceLastCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        """How many depositions have elapsed along this column's line of
        descent since the las matching strata at the same rank between self and
        other?

        Returns None if no common ancestor is shared between self and other.
        """

        last_common_rank = self.CalcRankOfLastCommonalityWith(other,)
        if last_common_rank is None: return None
        else:
            assert self.GetNumStrataDeposited()
            res = self.GetNumStrataDeposited() - 1 - last_common_rank
            assert 0 <= res < self.GetNumStrataDeposited()
            return res

    def CalcRanksSinceFirstDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        """How many depositions have elapsed along this column's line of
        descent since the first mismatching strata at the same rank between
        self and other?

        Returns
        -------
        int, optional
            The number of depositions elapsed or None if no disparity (i.e.,
            both columns have same number of strata deposited and the most
            recent stratum is common between self and other).

        Notes
        -----
        Returns -1 if self and other share no mismatching strata at common
        ranks but other has more strata deposited then self.
        """

        first_disparate_rank = self.CalcRankOfFirstDisparityWith(other,)
        if first_disparate_rank is None: return None
        else:
            assert self.GetNumStrataDeposited()
            res = self.GetNumStrataDeposited() - 1 - first_disparate_rank
            assert -1 <= res < self.GetNumStrataDeposited()
            return res

    def CalcRanksSinceMrcaBoundsWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[typing.Tuple[int, int]]:
        """Calculate bounds on estimate for the number of depositions elapsed
        along this column's line of descent since the most recent common
        ancestor with other.

        Returns
        -------
        (int, int), optional
            Inclusive lower bound and then exclusive upper bound on estimate or
            None if no common ancestor is shared between self and other.

        See Also
        --------
        CalcRanksSinceMrcaUncertaintyWith :
            Wrapper to report uncertainty of calculated bounds.
        """

        if self.HasAnyCommonAncestorWith(other):
            since_first_disparity = self.CalcRanksSinceFirstDisparityWith(other)
            lb_exclusive = opyt.or_value(since_first_disparity, -1)
            lb_inclusive = lb_exclusive + 1

            since_last_common = self.CalcRanksSinceLastCommonalityWith(other)
            ub_inclusive = since_last_common
            ub_exclusive = ub_inclusive + 1

            return (lb_inclusive, ub_exclusive)
        else:
            return None

    def CalcRanksSinceMrcaUncertaintyWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> int:
        """Calculate uncertainty of estimate for the number of depositions
        elapsed along this column's line of descent since the most common recent
        ancestor with other.

        Returns 0 if no common ancestor is shared between self and other.

        See Also
        --------
        CalcRanksSinceMrcaBoundsWith :
            Calculates bound whose uncertainty this method reports. See the
            corresponding docstring for explanation of parameters.
        """

        bounds = self.CalcRanksSinceMrcaBoundsWith(other)
        return 0 if bounds is None else abs(operator.sub(*bounds)) - 1

    def GetLastCommonStratumWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[HereditaryStratum]:
        """Get the most recent stratum in common between self and other, if any.

        Common strata share identical rank and differentia. Returns None if no
        common strata exist between the two columns.
        """

        rank = self.CalcRankOfLastCommonalityWith(other)
        if rank is not None:
            index = ip.popsingleton(
                index
                for index in range(self.GetNumStrataRetained())
                if rank == self.GetRankAtColumnIndex(index)
            )
            return self.GetStratumAtColumnIndex(index)
        else: return None

    def HasAnyCommonAncestorWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> bool:
        """Does self share any common ancestor with other?

        Note that stratum rention policies are strictly required to permanently
        retain the most ancient stratum.
        """

        first_disparity = self.CalcRankOfFirstDisparityWith(other)
        return True if first_disparity is None else first_disparity > 0

    def Clone(
            self: 'HereditaryStratigraphicColumn',
    ) -> 'HereditaryStratigraphicColumn':
        """Create a copy of the store with identical data that may be freely
        altered without affecting data within this store."""

        # shallow copy
        result = copy(self)
        # do semi-shallow duplication on select elements
        result._stratum_ordered_store = self._stratum_ordered_store.Clone()
        return result

    def CloneDescendant(
        self: 'HereditaryStratigraphicColumn',
        stratum_annotation: typing.Optional[typing.Any]=None,
    ) -> 'HereditaryStratigraphicColumn':
        """Return a cloned bundle that has had an additional stratum deposited.

        Does not alter self.

        Parameters
        ----------
        stratum_annotation: any, optional
            Optional object to store as an annotation. Allows arbitrary user-
            provided to be associated with this stratum deposition in the
            line of descent.
        """

        res = self.Clone()
        res.DepositStratum(annotation=stratum_annotation)
        return res

    def DiffRetainedRanks(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Tuple[typing.Set[int], typing.Set[int]]:
        """Return the set of ranks retained by self but not other and vice
        versa as a tuple."""

        self_ranks = set( self.GetRetainedRanks() )
        other_ranks = set( other.GetRetainedRanks() )

        return (
            self_ranks - other_ranks,
            other_ranks - self_ranks,
        )
