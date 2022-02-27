from collections import deque
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

    def CalcProbabilityDifferentiaCollision(
        self: 'HereditaryStratigraphicColumn',
    ) -> float:
        """What is the probability of two randomly-differentiated differentia
        being identical by coincidence?"""

        return 1.0 / 2**self._stratum_differentia_bit_width

    def CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
        self: 'HereditaryStratigraphicColumn',
        *,
        significance_level: float,
    ) -> float:
        """How many differentia collisions are required to reject the null
        hypothesis that columns do not share common ancestry at those ranks at
        significance level significance_level?"""

        assert 0.0 <= significance_level <= 1.0

        log_base = self.CalcProbabilityDifferentiaCollision()
        return int(math.ceil(
            math.log(significance_level, log_base)
        ))

    def CalcDefinitiveMaxRankOfLastRetainedCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        """At most, how many depositions elapsed along the columns' lines of
        descent before the last matching strata at the same rank between
        self and other?

        Returns
        -------
        int, optional
            The number of depositions elapsed or None if no common ancestor is
            shared between the columns.
        """

        confidence_level = 0.49
        assert self.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - confidence_level,
        ) == 1
        return self.CalcRankOfLastRetainedCommonalityWith(
            other,
            confidence_level=confidence_level,
        )

    def CalcRankOfLastRetainedCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        confidence_level: float=0.95,
    ) -> typing.Optional[int]:
        """How many depositions elapsed along the columns' lines of
        descent before the last matching strata at the same rank between
        self and other?

        Parameters
        ----------
        confidence_level : float, optional
            With what probability should the true rank of the last commonality
            with other fall at or after the returned rank? Default 0.95.

        Returns
        -------
        int, optional
            The number of depositions elapsed or None if no common ancestor is
            shared between the columns.

        Notes
        -----
        The true rank of the last commonality with other is guaranteed to never
        be after the returned rank when confidence_level < 0.5.
        """

        assert 0.0 <= confidence_level <= 1.0

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
            return self._do_generic_CalcRankOfLastRetainedCommonalityWith(
                other,
                confidence_level=confidence_level,
            )
        else:
            return self._do_binary_search_CalcRankOfLastRetainedCommonalityWith(
                other,
                confidence_level=confidence_level,
            )

    def _do_binary_search_CalcRankOfLastRetainedCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        confidence_level: float,
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

        collision_implausibility_threshold = self.\
            CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=1.0 - confidence_level,
        )
        assert collision_implausibility_threshold > 0
        if first_disparite_idx is None:
            # no disparate strata found
            # fall back to _do_generic_CalcRankOfLastRetainedCommonalityWith to handle
            # proper bookkeeping in this case while skipping most of the search
            return self._do_generic_CalcRankOfLastRetainedCommonalityWith(
                other,
                self_start_idx=upper_bound,
                other_start_idx=upper_bound,
                confidence_level=confidence_level,
            )
        elif first_disparite_idx >= collision_implausibility_threshold:
            # disparate strata found, following some common strata
            # ...discount collision_implausibility_threshold - 1 common strata
            # as potential spurious differentia collisions
            # ... must also subtract 1 (canceling out -1 above) to account for
            # moving from disparite stratum to preceding common stratum
            last_common_idx \
                = first_disparite_idx - collision_implausibility_threshold
            last_common_rank = self.GetRankAtColumnIndex(
                last_common_idx,
            )
            assert last_common_idx == last_common_rank
            return last_common_rank
        else:
            # no common strata between self and other
            # or not enough common strata to discount the possibility all
            # are spurious collisions with respect to the given confidence
            # level; conservatively conclude there is no common ancestor
            return None

    def _do_generic_CalcRankOfLastRetainedCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        *,
        self_start_idx: int=0,
        other_start_idx: int=0,
        confidence_level: float,
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

        # we need to keep track of enough ranks of last-seen common strata so
        # that we can discount this many (minus 1) as potentially occuring due
        # to spurious differentia collisions
        collision_implausibility_threshold = self.\
            CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=1.0 - confidence_level,
        )
        assert collision_implausibility_threshold > 0
        # holds up to n last-seen ranks with common strata,
        # with the newest last-seen rank at the front (index 0)
        # and the up to nth last-seen rank at the back (index -1)
        preceding_common_strata_ranks \
            = deque([], collision_implausibility_threshold)
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
                        preceding_common_strata_ranks.appendleft(self_cur_rank)
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
            try:
                # discount collision_implausibility_threshold - 1 common strata
                # as potential spurious differentia collisions
                return preceding_common_strata_ranks[
                    collision_implausibility_threshold - 1
                ]
            except IndexError:
                # not enough common strata to discount the possibility all
                # are spurious collisions with respect to the given confidence
                # level; conservatively conclude there is no common ancestor
                return None

    def CalcDefinitiveMaxRankOfFirstRetainedDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        """At most, how many depositions elapsed along the columns'
        lines of descent before the first mismatching strata at the same rank
        between self and other?

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

        confidence_level = 0.49
        assert self.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - confidence_level,
        ) == 1
        return self.CalcRankOfFirstRetainedDisparityWith(
            other,
            confidence_level=confidence_level,
        )

    def CalcRankOfFirstRetainedDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        confidence_level: float=0.95,
    ) -> typing.Optional[int]:
        """How many depositions elapsed along the columns' lines of
        descent before the first mismatching strata at the same rank between
        self and other?

        Parameters
        ----------
        confidence_level : float, optional
            With what probability should the true rank of the first disparity
            with other fall at or after the returned rank? Default 0.95.

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

        The true rank of the first disparity with other is guaranteed to never
        be after the returned rank when confidence_level < 0.5.
        """

        assert 0.0 <= confidence_level <= 1.0

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
            return self._do_generic_CalcRankOfFirstRetainedDisparityWith(
                other,
                confidence_level=confidence_level,
            )
        else:
            return self._do_binary_search_CalcRankOfFirstRetainedDisparityWith(
                other,
                confidence_level=confidence_level,
            )

    def _do_binary_search_CalcRankOfFirstRetainedDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        confidence_level: float,
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
            collision_plausibility_threshold = self.\
                CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                    significance_level=1.0 - confidence_level,
            ) - 1
            # discount collision_implausibility_threshold - 1 common
            # ranks due to potential spurious differentia collisions;
            # if not enough common ranks are available we still know
            # *definitively* that a disparity occured (because we
            # observed disparite strata at the same rank); so, make the
            # conservative assumption that the disparity occured as far
            # back as possible (rank 0)
            spurious_collision_corrected_idx = max(
                first_disparite_idx - collision_plausibility_threshold,
                0,
            )
            first_disparite_rank = self.GetRankAtColumnIndex(
                spurious_collision_corrected_idx
            )
            return first_disparite_rank
        else:
            # no disparate strata found
            # fall back to _do_generic_CalcRankOfFirstRetainedDisparityWith to
            # handle proper bookkeeping in this case while skipping most of the
            # search
            return self._do_generic_CalcRankOfFirstRetainedDisparityWith(
                other,
                self_start_idx=upper_bound,
                other_start_idx=upper_bound,
                confidence_level=confidence_level,
            )

    def _do_generic_CalcRankOfFirstRetainedDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        *,
        self_start_idx: int=0,
        other_start_idx: int=0,
        confidence_level: float,
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


        # we need to keep track of enough last-seen common ranks so that we
        # can discount this many (minus 1) as potentially occuring due to
        # spurious differentia collisions
        collision_implausibility_threshold = self.\
            CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=1.0 - confidence_level,
        )
        assert collision_implausibility_threshold > 0
        # holds up to n last-seen common ranks,
        # with the newest last-seen rank at the front (index 0)
        # and the up to nth last-seen rank at the back (index -1)
        preceding_common_ranks = deque([], collision_implausibility_threshold)
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
                    preceding_common_ranks.appendleft(self_cur_rank)
                else:
                    # mismatching differentiae at the same rank
                    preceding_common_ranks.appendleft(self_cur_rank)
                    assert 0 <= self_cur_rank < self.GetNumStrataDeposited()

                    # discount collision_implausibility_threshold - 1 common
                    # ranks due to potential spurious differentia collisions;
                    # if not enough common ranks are available we still know
                    # *definitively* that a disparity occured (because we
                    # observed disparite strata at the same rank); so, make the
                    # conservative assumption that the disparity occured as far
                    # back as possible (the oldest up to nth last-seen common
                    # rank, at the back of the deque)
                    return preceding_common_ranks[-1]
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
        confidence_level: float=0.95,
        bound_type: str='symmetric',
    ) -> typing.Optional[typing.Tuple[int, int]]:
        """Calculate bounds on estimate for the number of depositions elapsed
        along the line of descent before the most recent common ancestor with
        other.

        Parameters
        ----------
        confidence_level : float, optional
            Bounds must capture what probability of containing the true rank of
            the MRCA? Default 0.95.
        bound_type : {'symmetric', 'hard_upper_bound'}
            How should the bounds be constructed? If 'symmetric', then true rank
            of the MRCA will fall above or below the bounds with equal
            probability. If 'hard_upper_bound' then the true rank of the MRCA
            is guaranteed to never fall above the bounds but may fall below.
            Default 'symmetric'.

        Returns
        -------
        (int, int), optional
            Inclusive lower and then exclusive upper bound on estimate or None
            if no common ancestor between self and other can be resolved with
            sufficient confidence. (Sufficient confidence depends on
            bound_type.)

        See Also
        --------
        CalcRankOfMrcaUncertaintyWith :
            Wrapper to report uncertainty of calculated bounds.
        """

        assert 0.0 <= confidence_level <= 1.0
        significance_level = 1.0 - confidence_level

        if self.HasAnyCommonAncestorWith(
            other,
            confidence_level={
                'symmetric' : 1.0 - significance_level / 2.0,
                'hard_upper_bound' : 1.0 - significance_level,
            }[bound_type],
        ):
            first_disparity = {
                'symmetric' : lambda: self.CalcRankOfFirstRetainedDisparityWith(
                    other,
                    confidence_level=1.0 - significance_level/2.0
                ),
                'hard_upper_bound' : lambda: \
                    self.CalcDefinitiveMaxRankOfFirstRetainedDisparityWith(
                        other
                    ),
            }[bound_type]()
            if first_disparity is None:
                num_self_deposited = self.GetNumStrataDeposited()
                num_other_deposited = other.GetNumStrataDeposited()
                assert num_self_deposited == num_other_deposited
            last_commonality = self.CalcRankOfLastRetainedCommonalityWith(
                other,
                confidence_level={
                    'symmetric' : 1.0 - significance_level / 2.0,
                    'hard_upper_bound' : 1.0 - significance_level,
                }[bound_type],
            )
            assert last_commonality is not None
            return (
                last_commonality,
                opyt.or_value(first_disparity, self.GetNumStrataDeposited()),
            )
        else: return None

    def CalcRankOfMrcaUncertaintyWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        confidence_level: float=0.95,
        bound_type: str='symmetric',
    ) -> int:
        """Calculate uncertainty of estimate for the number of depositions
        elapsed along the line of descent before the most common recent
        ancestor with other.

        Returns 0 if no common ancestor between self and other can be resolved
        with sufficient confidence. (Sufficient confidence depends on
        bound_type.)

        See Also
        --------
        CalcRankOfMrcaBoundsWith :
            Calculates bound whose uncertainty this method reports. See the
            corresponding docstring for explanation of parameters.
        """

        bounds = self.CalcRankOfMrcaBoundsWith(
            other,
            confidence_level=confidence_level,
            bound_type=bound_type,
        )
        return 0 if bounds is None else abs(operator.sub(*bounds)) - 1

    def CalcDefinitiveMinRanksSinceLastRetainedCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        """At least, how many depositions have elapsed along this column's line
        of descent since the las matching strata at the same rank between self
        and other?

        Returns None if no common ancestor between self and other can be
        resolved with absolute confidence.
        """

        confidence_level = 0.49
        assert self.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - confidence_level,
        ) == 1
        return self.CalcRanksSinceLastRetainedCommonalityWith(
            self,
            confidence_level=confidence_level,
        )

    def CalcRanksSinceLastRetainedCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        confidence_level: float=0.95,
    ) -> typing.Optional[int]:
        """How many depositions have elapsed along this column's line of
        descent since the las matching strata at the same rank between self and
        other?

        Returns None if no common ancestor is shared between self and other.

        Parameters
        ----------
        confidence_level : float, optional
            With what probability should the true number of ranks since the
            last commonality with other be less than the calculated estimate?
            Default 0.95.

        Notes
        -----
        If confidence_level < 0.5, then the true number of ranks since the last
        commonality with other is guaranteed greater than or equal to the
        calculated estimate.
        """

        assert 0.0 <= confidence_level <= 1.0

        last_common_rank = self.CalcRankOfLastRetainedCommonalityWith(
            other,
            confidence_level=confidence_level,
        )
        if last_common_rank is None: return None
        else:
            assert self.GetNumStrataDeposited()
            res = self.GetNumStrataDeposited() - 1 - last_common_rank
            assert 0 <= res < self.GetNumStrataDeposited()
            return res

    def CalcDefinitiveMinRanksSinceFirstRetainedDisparityWith(
            self: 'HereditaryStratigraphicColumn',
            other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        """At least, how many depositions have elapsed along this column's line
        of descent since the first mismatching strata at the same rank between
        self and other?

        Returns None if no disparity found (i.e., both columns have same number
        of strata deposited and the most recent stratum is common between self
        and other).
        """

        confidence_level = 0.49
        assert self.CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1.0 - confidence_level,
        ) == 1
        return self.CalcRanksSinceFirstRetainedDisparityWith(
            other,
            confidence_level=confidence_level,
        )

    def CalcRanksSinceFirstRetainedDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        confidence_level: float=0.95,
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

        Parameters
        ----------
        confidence_level : float, optional
            With what probability should the true number of ranks since the
            first disparity be less than or equal to the returned estimate?
            Default 0.95.

        Notes
        -----
        Returns -1 if self and other share no mismatching strata at common
        ranks but other has more strata deposited then self.

        The true number of ranks since the first disparity with other is
        guaranteed strictly less than or equal to the returned estimate when
        confidence_level < 0.5.
        """

        first_disparate_rank = self.CalcRankOfFirstRetainedDisparityWith(
            other,
            confidence_level=confidence_level,
        )
        if first_disparate_rank is None: return None
        else:
            assert self.GetNumStrataDeposited()
            res = self.GetNumStrataDeposited() - 1 - first_disparate_rank
            assert -1 <= res < self.GetNumStrataDeposited()
            return res

    def CalcRanksSinceMrcaBoundsWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        confidence_level: float=0.95,
        bound_type: str='symmetric',
    ) -> typing.Optional[typing.Tuple[int, int]]:
        """Calculate bounds on estimate for the number of depositions elapsed
        along this column's line of descent since the most recent common
        ancestor with other.

        Parameters
        ----------
        confidence_level : float, optional
            With what probability should the true rank of the MRCA fall
            within the calculated bounds? Default 0.95.
        bound_type : {'symmetric', 'hard_lower_bound'}
            If 'symmetric', then the true number of ranks since the MRCA may
            lie on either side of the calculated bounds (i.e., may be less than
            the lower bound or greater than the upper bound). If
            'hard_lower_bound', then the true number of ranks since the MRCA is
            guaranteed to be strictly less than or  Default 'symmetric'.

        Returns
        -------
        (int, int), optional
            Inclusive lower bound and then exclusive upper bound on estimate or
            None if no common ancestor between self and other can be resolved
            with sufficient confidence. (Sufficient confidence depends on
            bound_type.)

        See Also
        --------
        CalcRanksSinceMrcaUncertaintyWith :
            Wrapper to report uncertainty of calculated bounds.
        """

        assert 0.0 <= confidence_level <= 1.0

        significance_level = 1 - confidence_level
        if self.HasAnyCommonAncestorWith(
            other,
            confidence_level={
                'symmetric' : 1.0 - significance_level / 2.0,
                'hard_lower_bound' : 1.0 - significance_level,
            }[bound_type],
        ):
            since_first_disparity = {
                'symmetric' : lambda: \
                    self.CalcRanksSinceFirstRetainedDisparityWith(
                        other,
                        confidence_level=1.0 - significance_level / 2.0,
                    ),
                'hard_lower_bound' : lambda: \
                    self.CalcDefinitiveMinRanksSinceFirstRetainedDisparityWith(
                        other
                    ),
            }[bound_type]()

            lb_exclusive = opyt.or_value(since_first_disparity, -1)
            lb_inclusive = lb_exclusive + 1

            since_last_commonality \
                = self.CalcRanksSinceLastRetainedCommonalityWith(
                    other,
                    confidence_level={
                        'symmetric' : 1.0 - significance_level / 2.0,
                        'hard_lower_bound' : 1.0 - significance_level,
                    }[bound_type],
                )
            assert since_last_commonality is not None
            ub_inclusive = since_last_commonality
            ub_exclusive = ub_inclusive + 1

            return (lb_inclusive, ub_exclusive)
        else:
            return None

    def CalcRanksSinceMrcaUncertaintyWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        confidence_level: float=0.95,
        bound_type: str='symmetric',
    ) -> int:
        """Calculate uncertainty of estimate for the number of depositions
        elapsed along this column's line of descent since the most common recent
        ancestor with other.

        Returns 0 if no common ancestor between self and other can be resolved
        with sufficient confidence. (Sufficient confidence depends on
        bound_type.)

        See Also
        --------
        CalcRanksSinceMrcaBoundsWith :
            Calculates bound whose uncertainty this method reports. See the
            corresponding docstring for explanation of parameters.
        """

        assert 0.0 <= confidence_level <= 1.0

        bounds = self.CalcRanksSinceMrcaBoundsWith(
            other,
            confidence_level=confidence_level,
            bound_type=bound_type,
        )
        return 0 if bounds is None else abs(operator.sub(*bounds)) - 1

    def GetLastCommonStratumWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        confidence_level: float=0.95,
    ) -> typing.Optional[HereditaryStratum]:
        """Get the most recent stratum in common between self and other, if any.

        Common strata share identical rank and differentia. Returns None if no
        common strata exist between the two columns. Allows probability equal
        to 1 - confidence_level that the last true common stratum is before the
        stratum returned (i.e., strata were erroneously detected as common due
        to spurious differentia collisions).

        See Also
        --------
        CalcRankOfLastRetainedCommonalityWith :
            Selects the stratum returned. See the corresponding docstring for
            explanation of parameters.
        """

        rank = self.CalcRankOfLastRetainedCommonalityWith(
            other,
            confidence_level=confidence_level,
        )
        if rank is not None:
            index = ip.popsingleton(
                index
                for index in range(self.GetNumStrataRetained())
                if rank == self.GetRankAtColumnIndex(index)
            )
            return self.GetStratumAtColumnIndex(index)
        else: return None

    def DefinitivelySharesNoCommonAncestorWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> bool:
        """Does self definitively share no common ancestor with other?

        Note that stratum rention policies are strictly required to permanently
        retain the most ancient stratum.

        See Also
        --------
        HasAnyCommonAncestorWith:
            Can we conclude with confidence_level confidence that self and other
            share a common ancestor?
        """

        first_disparity \
            = self.CalcDefinitiveMaxRankOfFirstRetainedDisparityWith(
                other,
                confidence_level=confidence_level,
            )
        return False if first_disparity is None else first_disparity == 0

    def HasAnyCommonAncestorWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        confidence_level: float=0.95,
    ) -> bool:
        """Does self share any common ancestor with other?

        Note that stratum rention policies are strictly required to permanently
        retain the most ancient stratum.

        Parameters
        ----------
        confidence_level : float, optional
            The probability that we will correctly conclude no common ancestor
            is shared with other if, indeed, no common ancestor is actually
            shared. Default 0.95.

        See Also
        --------
        DefinitivelySharesNoCommonAncestorWith :
            Can we definitively conclude that self and other share no common
            ancestor?
        """

        first_disparity = self.CalcRankOfFirstRetainedDisparityWith(
            other,
            confidence_level=confidence_level,
        )
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
