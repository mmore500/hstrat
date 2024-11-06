from copy import copy
import math
import operator
import sys
import typing
import warnings

from deprecated.sphinx import deprecated
from interval_search import binary_search
import opytional as opyt

from ..stratum_retention_strategy.stratum_retention_algorithms import (
    perfect_resolution_algo,
)
from ._HereditaryStratum import HereditaryStratum
from .stratum_ordered_stores import HereditaryStratumOrderedStoreList
from .stratum_ordered_stores._detail import HereditaryStratumOrderedStoreBase

# define type alias for ordered stores
OrderedStore = typing.Union[
    typing.Callable[..., HereditaryStratumOrderedStoreBase],
    typing.Tuple[HereditaryStratumOrderedStoreBase, int],
    None,
]


class HereditaryStratigraphicColumn:
    """Genetic annotation to enable phylogenetic inference.

    Primary end-user facing interface for hstrat library. Should be bundled with
    digital genomes and propagated via the CloneDescendant method when passing
    those genomes from parent to offspring. Provides basis for phylogenetic
    analysis of distributed digital evolution populations.

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

    __slots__ = (
        "_always_store_rank_in_stratum",
        "_stratum_differentia_bit_width",
        "_num_strata_deposited",
        "_stratum_ordered_store",
        "_stratum_retention_policy",
    )

    # if True, strata will be constructed with deposition rank stored even if
    # the stratum retention condemner does not require it
    _always_store_rank_in_stratum: bool
    # how many bits wide of differentia should the deposited strata be
    # constructed with?
    _stratum_differentia_bit_width: int
    # counter tracking the number of strata deposited
    # incremented *after* a deposition and its coinciding purge are complete
    _num_strata_deposited: int
    # data structure storing retained strata
    _stratum_ordered_store: typing.Any
    # functor specifying stratum retention policy
    _stratum_retention_policy: typing.Any

    def __init__(
        self: "HereditaryStratigraphicColumn",
        stratum_retention_policy: typing.Any = perfect_resolution_algo.Policy(),
        *,
        always_store_rank_in_stratum: bool = True,
        stratum_differentia_bit_width: int = 64,
        initial_stratum_annotation: typing.Optional[typing.Any] = None,
        stratum_ordered_store: OrderedStore = None,
        stratum_ordered_store_factory: OrderedStore = None,  # deprecated
    ):
        """Initialize column to track a new line of descent.

        Deposits a first stratum, so GetNumStrataDeposited() will return 1 after
        initialization even though the user has not yet called DepositStratum().

        Parameters
        ----------
        stratum_retention_policy : any
            Policy struct that implements stratum retention policy by specifying
            the set of strata ranks that should be pruned from a hereditary
            stratigraphic column when the nth stratum is deposited.
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
        stratum_ordered_store: callable or tuple of store and count, optional
            One of:
            * callable to generate a container that implements the necessary
            interface to store strata within the column; can be configured for
            performance reasons, but has no semantic effect.
            * instance of one aforementioned container along with a deposition count
            * None, in which case a default-initialized container will be used
        stratum_ordered_store_factory: deprecated, alias of stratum_ordered_store.

        Notes
        -----
        If no condemner or predicate functor specifying a stratum retention
        policy is provided, the perfect resolution policy where all strata are
        retained is used.
        """
        self._always_store_rank_in_stratum = always_store_rank_in_stratum
        self._stratum_differentia_bit_width = stratum_differentia_bit_width
        self._stratum_retention_policy = stratum_retention_policy

        if stratum_ordered_store_factory is not None:
            warnings.warn(
                """stratum_ordered_store_factory kwarg is deprecated.
                Please use stratum_ordered_store kwarg instead.""",
                DeprecationWarning,
            )
            # disallow mixed use of deprecated and replacement
            assert stratum_ordered_store is None
            stratum_ordered_store = stratum_ordered_store_factory

        if stratum_ordered_store is None:
            # if no hstrat ordered store is specified, we use a list
            stratum_ordered_store = HereditaryStratumOrderedStoreList
        if callable(stratum_ordered_store):
            # ordered store is actually an ordered store factory
            self._stratum_ordered_store = stratum_ordered_store()
            self._num_strata_deposited = 0
            self.DepositStratum(annotation=initial_stratum_annotation)
        elif isinstance(
            stratum_ordered_store[0], HereditaryStratumOrderedStoreBase
        ):
            # ordered store is already an instance of an ordered store
            (
                self._stratum_ordered_store,
                self._num_strata_deposited,
            ) = stratum_ordered_store
        else:
            raise ValueError(
                """stratum_ordered_store is of invalid type; \
            should be callable or tuple(callable instance, deposition count)"""
            )

    def __eq__(
        self: "HereditaryStratigraphicColumn",
        other: "HereditaryStratigraphicColumn",
    ) -> bool:
        """Compare for value-wise equality."""
        # adapted from https://stackoverflow.com/a/4522896
        return (
            isinstance(
                other,
                self.__class__,
            )
            and self.__slots__ == other.__slots__
            and all(
                getter(self) == getter(other)
                for getter in [
                    operator.attrgetter(attr) for attr in self.__slots__
                ]
            )
        )

    def _CanOmitStratumDepositionRank(
        self: "HereditaryStratigraphicColumn",
    ) -> bool:
        """Does the column's associated stratum retention policy provide
        calculation of the rank of a stratum as a function of its position?"""
        return self._stratum_retention_policy.CalcRankAtColumnIndex is not None

    def _ShouldOmitStratumDepositionRank(
        self: "HereditaryStratigraphicColumn",
    ) -> bool:
        """Decide if deposition rank should be stored in stratum.

        Implementation detail to inspect configured stratum retention policy
        and manual override to decide whether deposition rank should be stored
        as a data member of generated strata.

        Note that strata are not required to be stored if the stratum retention
        policy allows for the rank of a stratum to be calcualted as a function
        of its position within the column and the number of strata deposited
        onto the column. However, it may be beneficial to store the stratum
        anyways for performance reasons if this calculation is expenxive.
        """
        return (
            self._CanOmitStratumDepositionRank()
            and not self._always_store_rank_in_stratum
        )

    def _CreateStratum(
        self: "HereditaryStratigraphicColumn",
        deposition_rank: int,
        annotation: typing.Optional[typing.Any] = None,
        differentia: typing.Optional[int] = None,
    ) -> HereditaryStratum:
        """Create a hereditary stratum with stored configuration attributes."""
        return HereditaryStratum(
            annotation=annotation,
            deposition_rank=(
                # don't store deposition rank if we know how to
                # calcualte it from stratum's position in column
                None
                if self._ShouldOmitStratumDepositionRank()
                else deposition_rank
            ),
            differentia_bit_width=self._stratum_differentia_bit_width,
            differentia=differentia,
        )

    def DepositStratum(
        self: "HereditaryStratigraphicColumn",
        annotation: typing.Optional[typing.Any] = None,
    ) -> None:
        """Elapse a generation.

        Parameters
        ----------
        annotation: any, optional
            Optional object to store as an annotation. Allows arbitrary user-
            provided to be associated with this stratum deposition in the
            line of descent.
        """
        new_stratum = self._CreateStratum(
            deposition_rank=self._num_strata_deposited,
            annotation=annotation,
        )
        self._stratum_ordered_store.DepositStratum(
            rank=self._num_strata_deposited,
            stratum=new_stratum,
        )
        self._PurgeColumn()
        self._num_strata_deposited += 1

    def DepositStrata(
        self: "HereditaryStratigraphicColumn",
        num_stratum_depositions: int,
    ) -> None:
        """Elapse n generations.

        Parameters
        ----------
        num_stratum_depositions: int
            How many generations to elapse?
        """
        # fallback to naive approach if IterRetainedRanks not available
        policy = self._stratum_retention_policy
        if policy.IterRetainedRanks is None or num_stratum_depositions <= 1:
            for _ in range(num_stratum_depositions):
                self.DepositStratum()
            return

        prior_deposit_count = self.GetNumStrataDeposited()
        target_deposit_count = prior_deposit_count + num_stratum_depositions

        # for python 3.7+, dictionaries are guaranteed insertion ordered
        assert sys.version_info >= (3, 7)
        target_retained_ranks = {
            rank: None
            for rank in policy.IterRetainedRanks(target_deposit_count)
        }

        # delete no-longer-needed ranks
        self._stratum_ordered_store.DelRanks(
            ranks=(
                rank
                for rank in self.IterRetainedRanks()
                if rank not in target_retained_ranks
            ),
            get_column_index_of_rank=self.GetColumnIndexOfRank,
        )

        # add new retained ranks
        for rank in target_retained_ranks:
            if rank >= prior_deposit_count:
                self._stratum_ordered_store.DepositStratum(
                    rank=rank,
                    stratum=self._CreateStratum(rank),
                )

        # update generation counter
        self._num_strata_deposited += num_stratum_depositions

    def _PurgeColumn(self: "HereditaryStratigraphicColumn") -> None:
        """Discard stored strata according to the configured retention policy.

        Implementation detail. Called after a new stratum has been appended to
        the column's store but before it is considered fully deposited (i.e.,
        it is reflected in the column's internal deposition counter).
        """
        condemned_ranks = self._stratum_retention_policy.GenDropRanks(
            num_stratum_depositions_completed=self.GetNumStrataDeposited(),
            retained_ranks=self.IterRetainedRanks(),
        )
        self._stratum_ordered_store.DelRanks(
            ranks=condemned_ranks,
            get_column_index_of_rank=self.GetColumnIndexOfRank,
        )

    def IterRetainedRanks(
        self: "HereditaryStratigraphicColumn",
    ) -> typing.Iterator[int]:
        """Iterate over deposition ranks of strata stored in the column.

        The store may be altered during iteration without iterator
        invalidation, although subsequent updates will not be reflected in the
        iterator.
        """
        if self._ShouldOmitStratumDepositionRank():
            if hasattr(self._stratum_retention_policy, "IterRetainedRanks"):
                yield from self._stratum_retention_policy.IterRetainedRanks(
                    self.GetNumStrataDeposited()
                )
            else:
                for idx in range(self.GetNumStrataRetained()):
                    yield self.GetRankAtColumnIndex(idx)
        else:
            yield from self._stratum_ordered_store.IterRetainedRanks()

    def IterRetainedStrata(
        self: "HereditaryStratigraphicColumn",
    ) -> typing.Iterator[HereditaryStratum]:
        """Iterate over strata stored in the column.
        Strata yielded from most ancient to most recent.
        """
        yield from self._stratum_ordered_store.IterRetainedStrata()

    def IterRetainedDifferentia(
        self: "HereditaryStratigraphicColumn",
    ) -> typing.Iterator[int]:
        """Iterate over differentia of strata stored in the column.

        Differentia yielded from most ancient to most recent.
        """
        return map(lambda x: x.GetDifferentia(), self.IterRetainedStrata())

    def IterRankDifferentiaZip(
        self: "HereditaryStratigraphicColumn",
        copyable: bool = False,
    ) -> typing.Iterator[typing.Tuple[int, int]]:
        """Iterate over ranks of retained strata and their differentia.

        If `copyable`, return an iterator that can be copied to produce a new
        fully-independent iterator at the same position.

        Equivalent to `zip(col.IterRetainedRanks(),
        col.IterRetainedDifferentia())`, but may be more efficient.
        """
        res = self._stratum_ordered_store.IterRankDifferentiaZip(
            get_rank_at_column_index=(
                self.GetRankAtColumnIndex
                if self._ShouldOmitStratumDepositionRank()
                else None
            ),
        )
        if copyable:
            res = iter([*res])
        return res

    def HasAnyAnnotations(
        self: "HereditaryStratigraphicColumn",
    ) -> bool:
        """Do any retained strata have annotations?"""
        return any(
            stratum.GetAnnotation() is not None
            for stratum in self._stratum_ordered_store.IterRetainedStrata()
        )

    def GetNumStrataRetained(self: "HereditaryStratigraphicColumn") -> int:
        """How many strata are currently stored within the column?

        May be fewer than the number of strata deposited if strata have been
        discarded as part of the configured stratum retention policy.
        """
        return self._stratum_ordered_store.GetNumStrataRetained()

    def GetNumStrataDeposited(self: "HereditaryStratigraphicColumn") -> int:
        """How many strata have been depostited on the column?

        Note that a first stratum is deposited on the column during
        initialization.
        """
        return self._num_strata_deposited

    def GetStratumAtColumnIndex(
        self: "HereditaryStratigraphicColumn",
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

    def GetStratumAtRank(
        self: "HereditaryStratigraphicColumn",
        rank: int,
    ) -> typing.Optional[HereditaryStratum]:
        """Get the stratum deposited at generation g.

        Returns None if stratum with rank g is not retained.
        """
        return opyt.apply_if(
            self.GetColumnIndexOfRank(rank),
            self.GetStratumAtColumnIndex,
        )

    def GetRankAtColumnIndex(
        self: "HereditaryStratigraphicColumn",
        index: int,
    ) -> int:
        """Map column position to generation of deposition.

        What is the deposition rank of the stratum positioned at index i
        among retained strata? Index order is from most ancient (index 0) to
        most recent.
        """
        if self._ShouldOmitStratumDepositionRank():
            return self._stratum_retention_policy.CalcRankAtColumnIndex(
                index=index,
                num_strata_deposited=self.GetNumStrataDeposited(),
            )
        else:
            # fall back to store lookup
            return self._stratum_ordered_store.GetRankAtColumnIndex(index)

    def GetColumnIndexOfRank(
        self: "HereditaryStratigraphicColumn",
        rank: int,
    ) -> typing.Optional[int]:
        """Map generation of deposition to column position.

        What is the index position within retained strata of the stratum
        deposited at rank r? Returns None if no stratum with rank r is present
        within the store.
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
        self: "HereditaryStratigraphicColumn",
    ) -> int:
        """How many deposited strata have been discarded?

        Determined by number of generations elapsed and the configured column
        retention policy.
        """
        return self.GetNumStrataDeposited() - self.GetNumStrataRetained()

    def GetStratumDifferentiaBitWidth(
        self: "HereditaryStratigraphicColumn",
    ) -> int:
        """How many bits wide are the differentia of strata?"""
        return self._stratum_differentia_bit_width

    def HasDiscardedStrata(
        self: "HereditaryStratigraphicColumn",
    ) -> bool:
        """Have any deposited strata been discarded?"""
        return self.GetNumDiscardedStrata() > 0

    @deprecated(
        version="1.6.0",
        reason="Use calc_probability_differentia_collision_between",
    )
    def CalcProbabilityDifferentiaCollision(
        self: "HereditaryStratigraphicColumn",
    ) -> float:
        """How likely are differentia collisions?

        Calculates the probability of two randomly-differentiated differentia
        being identical by coincidence.
        """
        return 1.0 / 2**self._stratum_differentia_bit_width

    @deprecated(
        version="1.6.0",
        reason="Use "
        "calc_min_implausible_spurious_differentia_collisions_between",
    )
    def CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
        self: "HereditaryStratigraphicColumn",
        significance_level: float,
    ) -> int:
        """Determine amount of evidence required to indicate shared ancestry.

        Calculates how many differentia collisions are required to reject the
        null hypothesis that columns do not share common ancestry at those
        ranks at significance level significance_level.
        """
        assert 0.0 <= significance_level <= 1.0

        log_base = self.CalcProbabilityDifferentiaCollision()
        return int(math.ceil(math.log(significance_level, log_base)))

    def Clone(
        self: "HereditaryStratigraphicColumn",
    ) -> "HereditaryStratigraphicColumn":
        """Create an independent copy of the column.

        Contains identical data but may be freely altered without affecting
        data within this column.
        """
        # shallow copy
        result = copy(self)
        # do semi-shallow duplication on select elements
        result._stratum_ordered_store = self._stratum_ordered_store.Clone()
        return result

    def CloneDescendant(
        self: "HereditaryStratigraphicColumn",
        stratum_annotation: typing.Optional[typing.Any] = None,
    ) -> "HereditaryStratigraphicColumn":
        """Return a cloned column that has had an additional stratum deposited.

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

    def CloneNthDescendant(
        self: "HereditaryStratigraphicColumn",
        num_stratum_depositions: int,
    ) -> "HereditaryStratigraphicColumn":
        """Return a cloned column that has had n additional strata deposited.

        Does not alter self.

        Parameters
        ----------
        num_stratum_depositions: int
            How many generations should clone column be descended?
        """
        res = self.Clone()
        res.DepositStrata(num_stratum_depositions)
        return res
