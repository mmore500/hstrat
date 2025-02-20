from copy import deepcopy
import operator
import random
import typing

from downstream import dsurf

from ._HereditaryStratum import HereditaryStratum
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
        "_differentia_bit_width",
        "_surface",
    )

    # how many bits wide of differentia should the deposited strata be
    # constructed with?
    _differentia_bit_width: int

    # stores the actual downstream surface
    _surface: dsurf.Surface[int]

    def __init__(
        self: "HereditaryStratigraphicColumn",
        dstream_surface: dsurf.Surface[int],
        *,
        stratum_differentia_bit_width: int = 64,
    ) -> None:
        """A wrapper around the downstream Surface object to fit the
        `hstrat` interface.

        Initially depoists `S` strata, where `S` is the surface size.

        Parameters
        ----------
        dstream_surface: downstream.dsurf.Surface
            The surface to use to store annotations.
        stratum_differentia_bit_width : int, optional
            The bit width of the generated differentia. Default 64, allowing
            for 2^64 distinct values.
        """
        self._surface = dstream_surface
        self._differentia_bit_width = stratum_differentia_bit_width
        self.DepositStrata(self._surface.S)

    def __eq__(
        self: "HereditaryStratigraphicColumn",
        other: typing.Any,
    ) -> bool:
        """Compare for value-wise equality."""
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

    def _CreateStratum(
        self: "HereditaryStratigraphicColumn",
    ) -> int:
        """Create a hereditary stratum with stored configuration attributes."""
        return random.randrange(2**self._differentia_bit_width)

    def DepositStratum(
        self: "HereditaryStratigraphicColumn",
    ) -> None:
        """Elapse a generation by depositing a differentia value."""
        self._surface.ingest(self._CreateStratum())

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
        self._surface.ingest_multiple(
            num_stratum_depositions, lambda _: self._CreateStratum()
        )

    def IterRetainedRanks(
        self: "HereditaryStratigraphicColumn",
    ) -> typing.Iterator[int]:
        """Iterate over deposition ranks of strata stored in the column.

        The store may be altered during iteration without iterator
        invalidation, although subsequent updates will not be reflected in the
        iterator.
        """
        return (
            t - self._surface.S
            for t in sorted(self._surface.lookup_retained())
        )

    def IterRetainedStrata(
        self: "HereditaryStratigraphicColumn",
    ) -> typing.Iterator[HereditaryStratum]:
        """Iterate over strata stored in the column.
        Strata yielded from most ancient to most recent.
        """
        return (
            HereditaryStratum(
                annotation=None,
                deposition_rank=t - self._surface.S,
                differentia_bit_width=self._differentia_bit_width,
                differentia=v,
            )
            for t, v in sorted(self._surface.enumerate_retained())
        )

    def IterRetainedDifferentia(
        self: "HereditaryStratigraphicColumn",
    ) -> typing.Iterator[int]:
        """Iterate over differentia of strata stored in the column.

        Differentia yielded from most ancient to most recent.
        """
        return (v for _, v in sorted(self._surface.enumerate_retained()))

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
        res = (
            (t - self._surface.S, v)
            for t, v in sorted(self._surface.enumerate_retained())
        )
        if copyable:
            return iter([*res])
        return res

    def HasAnyAnnotations(
        self: "HereditaryStratigraphicColumn",
    ) -> bool:
        """Do any retained strata have annotations?"""
        return False

    def GetNumStrataRetained(self: "HereditaryStratigraphicColumn") -> int:
        """How many strata are currently stored within the column?

        May be fewer than the number of strata deposited if strata have been
        discarded as part of the configured stratum retention policy.
        """
        return len([*self._surface.lookup_retained()])

    def GetNumStrataDeposited(self: "HereditaryStratigraphicColumn") -> int:
        """How many strata have been depostited on the column?

        Note that a first stratum is deposited on the column during
        initialization.
        """
        return self._surface.T

    def GetStratumAtColumnIndex(
        self: "HereditaryStratigraphicColumn",
        index: int,
    ) -> HereditaryStratum:
        """Get the stratum positioned at index i among retained strata.

        Index order is from most ancient (index 0) to most recent.
        """
        return [*self.IterRetainedStrata()][index]

    def GetStratumAtRank(
        self: "HereditaryStratigraphicColumn",
        rank: int,
    ) -> typing.Optional[HereditaryStratum]:
        """Get the stratum deposited at generation g.

        Returns None if stratum with rank g is not retained.
        """
        for s in self.IterRetainedStrata():
            if s.GetDepositionRank() == rank:
                return s
        return None

    def GetRankAtColumnIndex(
        self: "HereditaryStratigraphicColumn",
        index: int,
    ) -> int:
        """Map column position to generation of deposition.

        What is the deposition rank of the stratum positioned at index i
        among retained strata? Index order is from most ancient (index 0) to
        most recent.
        """
        return [*self.IterRetainedRanks()][index]

    def GetColumnIndexOfRank(
        self: "HereditaryStratigraphicColumn",
        rank: int,
    ) -> typing.Optional[int]:
        """Map generation of deposition to column position.

        What is the index position within retained strata of the stratum
        deposited at rank r? Returns None if no stratum with rank r is present
        within the store.
        """
        for i, r in enumerate(self.IterRetainedRanks()):
            if r == rank:
                return i
        return None

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
        return self._differentia_bit_width

    def HasDiscardedStrata(
        self: "HereditaryStratigraphicColumn",
    ) -> bool:
        """Have any deposited strata been discarded?"""
        return self.GetNumDiscardedStrata() > 0

    def Clone(
        self: "HereditaryStratigraphicColumn",
    ) -> "HereditaryStratigraphicColumn":
        """Create an independent copy of the column.

        Contains identical data but may be freely altered without affecting
        data within this column.
        """
        return deepcopy(self)

    def CloneDescendant(
        self: "HereditaryStratigraphicColumn",
    ) -> "HereditaryStratigraphicColumn":
        """Return a cloned column that has had an additional stratum deposited.

        Does not alter self.
        """
        new = self.Clone()
        new.DepositStratum()
        return new

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
        new = self.Clone()
        new.DepositStrata(num_stratum_depositions)
        return new
