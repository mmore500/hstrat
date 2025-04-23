from __future__ import annotations

from copy import deepcopy
import random
import types
import typing

from downstream import dsurf
import opytional as opyt

from ._HereditaryStratum import HereditaryStratum


class HereditaryStratigraphicSurface:
    """Wrapper around `downstream.dsurf.Surface` that supports the same
    interface as `HereditaryStratigraphicColumn`.

    Assumes that surface is initialized filled with differentiae, meaning that
    dstream T values are offset from rank/number of items deposited by surface
    size S. This also means that preinitialized-differentia have negative rank.
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

    @staticmethod
    def from_hex(
        hex_string: str,
        dstream_algo: types.ModuleType,
        *,
        dstream_S: int,
        dstream_storage_bitoffset: int,
        dstream_storage_bitwidth: int,
        dstream_T_bitoffset: int,
        dstream_T_bitwidth: int,
    ) -> "HereditaryStratigraphicSurface":
        """
        Deserialize a HereditaryStratigraphicSurface object from a hex string
        representation.

        Hex string representation needs exactly two contiguous parts:
        1. dstream_T (which is the number of depositions elapsed), and
        2. dstream_storage (which holds all the stored differentiae).

        Data in hex string representation should use big-endian byte order.

        Parameters
        ----------
        hex_string: str
            Hex string to be parsed, which can be uppercase or lowercase.
        dstream_algo: module
            Dstream algorithm for curation of retained differentia.
        dstream_storage_bitoffset: int
            Number of bits before the storage.
        dstream_storage_bitwidth: int
            Number of bits used for storage.
        dstream_T_bitoffset: int
            Number of bits before dstream_T.
        dstream_T_bitwidth: int
            Number of bits used to store dstream_T.
        dstream_S: int
            Number of buffer sites available to store differentiae.

            Determines how many differentiae are unpacked from storage.

        See Also
        --------
        HereditaryStratigraphicSurface.to_hex()
            Serialize a surface into a hex string.
        """
        return HereditaryStratigraphicSurface(
            dsurf.Surface.from_hex(
                hex_string,
                dstream_algo,
                S=dstream_S,
                storage_bitoffset=dstream_storage_bitoffset,
                storage_bitwidth=dstream_storage_bitwidth,
                T_bitoffset=dstream_T_bitoffset,
                T_bitwidth=dstream_T_bitwidth,
            ),
        )

    def to_hex(self, *, dstream_T_bitwidth: int = 32) -> str:
        """
        Serialize a HereditaryStratigraphicSurface object into a hex string
        representation.

        Serialized data comprises two components:
            1. dstream_T (the number of depositions elapsed) and
            2. dstream_storage (binary data of differentia values).

        The hex layout used is:

            0x...
              ########**************************************************
              ^                                                    ^
           dstream_T, length = `dstream_T_bitwidth` / 4            |
                                                                   |
              dstream_storage, length = `item_bitwidth` / 4 * dstream_S

        This hex string can be reconstituted into a
        HereditaryStratigraphicSurface object by calling
        `HereditaryStratigraphicSurface.from_hex()` with the following
        parameters:
            - `dstream_T_bitoffset` = 0
            - `dstream_T_bitwidth` = `dstream_T_bitwidth`
            - `dstream_storage_bitoffset` = `dstream_T_bitwidth`
            - `dstream_storage_bitwidth` = `self.S * item_bitwidth`

        Parameters
        ----------
        item_bitwidth: int
            Number of storage bits used per differentia.
        dstream_T_bitwidth: int, default 32
            Number of bits used to store count of elapsed depositions.

        See Also
        --------
        Surface.from_hex()
            Deserialize a surface from a hex string.
        """
        return self._surface.to_hex(
            item_bitwidth=self._differentia_bit_width,
            T_bitwidth=dstream_T_bitwidth,
        )

    def __init__(
        self: "HereditaryStratigraphicSurface",
        dstream_surface: dsurf.Surface[int],
        *,
        stratum_differentia_bit_width: int = 64,
    ) -> None:
        """A wrapper around the downstream Surface object to match the
        `hstrat.HereditaryStratigraphicColumn` interface.

        Initially depoists `S + 1` strata, where `S` is the surface size.

        Parameters
        ----------
        dstream_surface: downstream.dsurf.Surface
            The surface to use to store annotations.
        stratum_differentia_bit_width : int, default 64
            The bit width for generated differentia.
        """
        self._surface = dstream_surface
        self._differentia_bit_width = stratum_differentia_bit_width
        if dstream_surface.T == 0:
            self.DepositStrata(self._surface.S + 1)  # +1 matches col behavior
            assert self.GetNextRank() == 1
        elif dstream_surface.T < self._surface.S:
            raise ValueError("Partially-initialized Surface provided.")

    @property
    def S(self):
        """Number of buffer sites available to store differentiae."""
        return self._surface.S

    def __eq__(
        self: "HereditaryStratigraphicSurface",
        other: typing.Any,
    ) -> bool:
        """Compare two HereditaryStratigraphicSurface objects by value."""
        if not isinstance(other, HereditaryStratigraphicSurface):
            return False
        return (
            self._surface == other._surface
            and self._differentia_bit_width == other._differentia_bit_width
        )

    def _CreateStratum(
        self: "HereditaryStratigraphicSurface",
        deposition_rank: typing.Optional[int] = None,  # noqa: ARG001
        # ^ no-op for column interface compat
        *,
        differentia: typing.Optional[int] = None,
    ) -> int:
        """Create a hereditary stratum with stored configuration attributes."""
        return opyt.or_value(
            differentia,
            random.randrange(2**self._differentia_bit_width),
        )

    def DepositStratum(
        self: "HereditaryStratigraphicSurface",
        differentia: typing.Optional[int] = None,
    ) -> None:
        """Elapse a generation by depositing a differentia value.

        Differentia may be provided (useful for testing) or, by default,
        randomly generated.
        """
        if (
            differentia is not None
            and int(differentia).bit_length() > self._differentia_bit_width
        ):
            raise ValueError(
                f"Differentia {differentia} is too large for "
                f"{self._differentia_bit_width} bit width.",
            )
        self._surface.ingest_one(
            opyt.or_else(differentia, self._CreateStratum),
        )

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
        """Iterate over deposition ranks of strata stored in the surface.

        The store may be altered during iteration without iterator
        invalidation, although subsequent updates will not be reflected in the
        iterator.
        """
        return (r for r, __ in self.IterRankDifferentiaZip())

    def IterRetainedStrata(
        self: "HereditaryStratigraphicSurface",
    ) -> typing.Iterator[HereditaryStratum]:
        """Iterate over strata stored in the surface.

        Strata are yielded from most ancient to most recent.
        """
        return (
            HereditaryStratum(
                annotation=None,
                deposition_rank=r,
                differentia_bit_width=self._differentia_bit_width,
                differentia=d,
            )
            for r, d in self.IterRankDifferentiaZip()
        )

    def IterRetainedDifferentia(
        self: "HereditaryStratigraphicSurface",
    ) -> typing.Iterator[int]:
        """Iterate over differentia of strata stored in the surface.

        Differentia yielded from most ancient to most recent.
        """
        return (d for __, d in self.IterRankDifferentiaZip())

    def IterRankDifferentiaZip(
        self: "HereditaryStratigraphicSurface",
        copyable: bool = False,  # noqa: ARG001 ... no-op for interface compat
    ) -> typing.Iterator[typing.Tuple[int, int]]:
        """Iterate over ranks of retained strata and their differentia.

        If `copyable`, return an iterator that can be copied to produce a new
        fully-independent iterator at the same position.

        Equivalent to `zip(surf.IterRetainedRanks(),
        surf.IterRetainedDifferentia())`.
        """

        return iter(
            sorted(
                (T - self._surface.S, v)
                for T, v in self._surface.lookup_zip_items(include_empty=False)
            ),
        )

    def HasAnyAnnotations(
        self: "HereditaryStratigraphicSurface",
    ) -> bool:
        """Do any retained strata have annotations?"""
        return False  # annotation feature not supported

    def GetNextRank(self: "HereditaryStratigraphicSurface") -> int:
        """Get the rank of the next stratum to be deposited.

        This is the rank of the next stratum to be deposited, not the rank of
        the most recent stratum.
        """
        return self._surface.T - self._surface.S

    def GetNumStrataRetained(self: "HereditaryStratigraphicSurface") -> int:
        """How many strata are currently stored within the surface?

        May be fewer than the number of strata deposited if strata have been
        discarded as part of the configured stratum retention policy.
        """
        return min(self._surface.T, self._surface.S)

    def GetNumStrataDeposited(self: "HereditaryStratigraphicSurface") -> int:
        """How many strata have been depostited on the surface?

        Note that a first `S` strata may be deposited on the surface during
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
        r = [*self._surface.lookup(include_empty=True)][index]
        return r if r is None else r - self._surface.S

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
            if r is not None and r == rank + self._surface.S:
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
        retention policy. Does not include `S` initialization strata.
        """
        return max(
            self.GetNumStrataDeposited()
            - self.GetNumStrataRetained()
            - self.S,
            0,
        )

    def GetStratumDifferentiaBitWidth(
        self: "HereditaryStratigraphicSurface",
    ) -> int:
        """How many bits wide are the differentia of strata?"""
        return self._differentia_bit_width

    def HasDiscardedStrata(
        self: "HereditaryStratigraphicSurface",
    ) -> bool:
        """Have any deposited strata been discarded?

        Does not include `S` initialization strata."""
        return self.GetNumDiscardedStrata() > 0

    def Clone(
        self: "HereditaryStratigraphicSurface",
    ) -> "HereditaryStratigraphicSurface":
        """Create an independent copy of the surface.

        Contains identical data but may be freely altered without affecting
        data within this surface.
        """
        return deepcopy(self)

    def CloneDescendant(
        self: "HereditaryStratigraphicSurface",
    ) -> "HereditaryStratigraphicSurface":
        """Return a cloned surface that has had an additional stratum deposited.

        Does not alter self.
        """
        new = self.Clone()
        new.DepositStratum()
        return new

    def CloneNthDescendant(
        self: "HereditaryStratigraphicSurface",
        num_stratum_depositions: int,
    ) -> "HereditaryStratigraphicSurface":
        """Return a cloned surface that has had n additional strata deposited.

        Does not alter self.

        Parameters
        ----------
        num_stratum_depositions: int
            How many generations should clone surface be descended?
        """
        new = self.Clone()
        new.DepositStrata(num_stratum_depositions)
        return new
