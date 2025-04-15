from __future__ import annotations

from copy import deepcopy
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


class HereditaryStratigraphicSurface:
    """
    A wrapper around `downstream.dsurf.Surface` that supports the same
    interface as `HereditaryStratigraphicColumn`.
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
        self: "HereditaryStratigraphicSurface",
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

    @property
    def S(self):
        return self._surface.S

    def __eq__(
        self: "HereditaryStratigraphicSurface",
        other: typing.Any,
    ) -> bool:
        if not isinstance(other, HereditaryStratigraphicSurface):
            return False
        return (
            self._surface == other._surface
            and self._differentia_bit_width == other._differentia_bit_width
        )

    def _CreateStratum(
        self: "HereditaryStratigraphicSurface",
    ) -> int:
        """Create a hereditary stratum with stored configuration attributes."""
        return random.randrange(2**self._differentia_bit_width)

    def DepositStratum(
        self: "HereditaryStratigraphicSurface",
    ) -> None:
        """Elapse a generation by depositing a differentia value."""
        self._surface.ingest_one(self._CreateStratum())

    def DepositStrata(
        self: "HereditaryStratigraphicSurface",
        num_stratum_depositions: int,
    ) -> None:
        """Elapse n generations.

        Parameters
        ----------
        num_stratum_depositions: int
            How many generations to elapse?
        """
        self._surface.ingest_many(
            num_stratum_depositions, lambda _: self._CreateStratum()
        )

    def IterRetainedRanks(
        self: "HereditaryStratigraphicSurface",
    ) -> typing.Iterator[int]:
        """Iterate over deposition ranks of strata stored in the column.

        The store may be altered during iteration without iterator
        invalidation, although subsequent updates will not be reflected in the
        iterator.
        """
        return (
            t - self._surface.S
            for t in sorted(self._surface.lookup(include_empty=False))
        )

    def IterRetainedStrata(
        self: "HereditaryStratigraphicSurface",
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
            for t, v in sorted(
                self._surface.lookup_zip_items(include_empty=False)
            )
        )

    def IterRetainedDifferentia(
        self: "HereditaryStratigraphicSurface",
    ) -> typing.Iterator[int]:
        """Iterate over differentia of strata stored in the column.

        Differentia yielded from most ancient to most recent.
        """
        return (
            v
            for _, v in sorted(
                self._surface.lookup_zip_items(include_empty=False)
            )
        )

    def IterRankDifferentiaZip(
        self: "HereditaryStratigraphicSurface",
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
            for t, v in sorted(
                self._surface.lookup_zip_items(include_empty=False)
            )
        )
        if copyable:
            return iter([*res])
        return res

    def HasAnyAnnotations(
        self: "HereditaryStratigraphicSurface",
    ) -> bool:
        """Do any retained strata have annotations?"""
        return False

    def GetNumStrataRetained(self: "HereditaryStratigraphicSurface") -> int:
        """How many strata are currently stored within the column?

        May be fewer than the number of strata deposited if strata have been
        discarded as part of the configured stratum retention policy.
        """
        return len([*self._surface.lookup(include_empty=False)])

    def GetNumStrataDeposited(self: "HereditaryStratigraphicSurface") -> int:
        """How many strata have been depostited on the column?

        Note that a first stratum is deposited on the column during
        initialization.
        """
        return self._surface.T

    def GetStratumAtColumnIndex(
        self: "HereditaryStratigraphicSurface",
        index: int,
    ) -> HereditaryStratum:
        """Get the stratum positioned at index i among retained strata.

        Index order is from most ancient (index 0) to most recent.
        """
        return [*self.IterRetainedStrata()][index]

    def GetStratumAtRank(
        self: "HereditaryStratigraphicSurface",
        rank: int,
    ) -> typing.Optional[HereditaryStratum]:
        """Get the stratum deposited at generation g.

        Returns None if stratum with rank g is not retained.
        """
        for s in self.IterRetainedStrata():
            if s.GetDepositionRank() == rank:
                return s
        return None

    def GetRankAtStorageIndex(
        self: "HereditaryStratigraphicSurface",
        index: int,
    ) -> typing.Optional[int]:
        """Map column position to generation of deposition.

        What is the deposition rank of the stratum positioned at index i
        among retained strata? Index order is from most ancient (index 0) to
        most recent.
        """
        return [*self._surface.lookup(include_empty=True)][index]

    def GetRankAtColumnIndex(
        self: "HereditaryStratigraphicSurface",
        index: int,
    ) -> int:
        """Map column position to generation of deposition.

        What is the deposition rank of the stratum positioned at index i
        among retained strata? Index order is from most ancient (index 0) to
        most recent.
        """
        return [*self.IterRetainedRanks()][index]

    def GetStorageIndexOfRank(
        self: "HereditaryStratigraphicSurface",
        rank: int,
    ) -> typing.Optional[int]:
        """Map generation of deposition to position within surface storage.

        What is the surface position within retained strata of the stratum
        deposited at rank r? Returns None if no stratum with rank r is present
        within the store.
        """
        for i, r in enumerate(self._surface.lookup(include_empty=True)):
            if r is not None and r == rank:
                return i
        return None

    def GetColumnIndexOfRank(
        self: "HereditaryStratigraphicSurface",
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
        self: "HereditaryStratigraphicSurface",
    ) -> int:
        """How many deposited strata have been discarded?

        Determined by number of generations elapsed and the configured column
        retention policy.
        """
        return self.GetNumStrataDeposited() - self.GetNumStrataRetained()

    def GetStratumDifferentiaBitWidth(
        self: "HereditaryStratigraphicSurface",
    ) -> int:
        """How many bits wide are the differentia of strata?"""
        return self._differentia_bit_width

    def HasDiscardedStrata(
        self: "HereditaryStratigraphicSurface",
    ) -> bool:
        """Have any deposited strata been discarded?"""
        return self.GetNumDiscardedStrata() > 0

    def Clone(
        self: "HereditaryStratigraphicSurface",
    ) -> "HereditaryStratigraphicSurface":
        """Create an independent copy of the column.

        Contains identical data but may be freely altered without affecting
        data within this column.
        """
        return deepcopy(self)

    def CloneDescendant(
        self: "HereditaryStratigraphicSurface",
    ) -> "HereditaryStratigraphicSurface":
        """Return a cloned column that has had an additional stratum deposited.

        Does not alter self.
        """
        new = self.Clone()
        new.DepositStratum()
        return new

    def CloneNthDescendant(
        self: "HereditaryStratigraphicSurface",
        num_stratum_depositions: int,
    ) -> "HereditaryStratigraphicSurface":
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
