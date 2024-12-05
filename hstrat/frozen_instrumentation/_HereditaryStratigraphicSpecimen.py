import typing

import numpy as np
import pandera as pa

from .._auxiliary_lib import CopyableSeriesItemsIter

_unsigned_integer_series_t = typing.Union[
    pa.typing.Series[pa.typing.UInt8()],
    pa.typing.Series[pa.typing.UInt16()],
    pa.typing.Series[pa.typing.UInt32()],
    pa.typing.Series[pa.typing.UInt64()],
]


class HereditaryStratigraphicSpecimen:
    """Postprocessing representation of the differentia retained by an extant
    HereditaryStratigraphicColumn, indexed by deposition rank.

    All entries correspond to retained differentia (i.e., no entries are null).

    See Also
    --------
    HereditaryStratigraphicAssemblageSpecimen
        Specimen representation that allows for easier alignment among members
        of a population without perfectly homogeneous retained ranks.
    specimen_from_records
        Deserialize a `HereditaryStratigraphicSpecimen` from a dict composed of
        builtin data types.
    col_to_specimen
        Create a `HereditaryStratigraphicSpecimen` from a
        `HereditaryStratigraphicColumn`.
    """

    __slots__ = ("_data", "_stratum_differentia_bit_width")

    _data: _unsigned_integer_series_t
    _stratum_differentia_bit_width: int

    def __init__(
        self: "HereditaryStratigraphicSpecimen",
        stratum_differentia_series: _unsigned_integer_series_t,
        stratum_differentia_bit_width: int,
    ) -> None:
        """Initialize a HereditaryStratigraphicSpecimen object with a sequence
        of rank-indexed differentia and a differentia bit width."""
        self._data = stratum_differentia_series
        self._stratum_differentia_bit_width = stratum_differentia_bit_width

        assert self._data.index.dtype in (
            "int8",
            "uint8",
            "int16",
            "uint16",
            "int32",
            "uint32",
            "int64",
            "uint64",
        )
        self._data.index.astype(np.uint64, copy=False)

    def GetStratumDifferentiaBitWidth(
        self: "HereditaryStratigraphicSpecimen",
    ) -> int:
        """How many bits wide are the differentia of strata?"""
        return self._stratum_differentia_bit_width

    def GetNumStrataDeposited(
        self: "HereditaryStratigraphicSpecimen",
    ) -> int:
        """How many strata have been depostited on the column?

        Note that a first stratum is deposited on the column during
        initialization.
        """
        assert self._data.index.dtype in (
            "int8",
            "uint8",
            "int16",
            "uint16",
            "int32",
            "uint32",
            "int64",
            "uint64",
        )
        # self._data.index[-1] is integral
        # must convert to int, or (at least sometimes) float results after + 1
        return int(self._data.index[-1]) + 1

    def GetNumStrataRetained(
        self: "HereditaryStratigraphicSpecimen",
    ) -> int:
        """How many strata are currently stored within the column?

        May be fewer than the number of strata deposited if strata have been
        discarded as part of the configured stratum retention policy.
        """
        return len(self._data)

    def GetNumDiscardedStrata(
        self: "HereditaryStratigraphicSpecimen",
    ) -> int:
        """How many deposited strata have been discarded?

        Determined by number of generations elapsed and the configured column
        retention policy.
        """
        return self.GetNumStrataDeposited() - self.GetNumStrataRetained()

    def HasDiscardedStrata(
        self: "HereditaryStratigraphicSpecimen",
    ) -> bool:
        """Have any deposited strata been discarded?"""
        return self.GetNumDiscardedStrata() > 0

    def GetData(
        self: "HereditaryStratigraphicSpecimen",
    ) -> _unsigned_integer_series_t:
        """Get the underlying Pandas Series containing differentia values
        indexed by rank.

        Notes
        -----
        This function directly returns the specimen's underlying Series
        data, so mutation of the returned object will alter or invalidate this
        specimen.
        """
        return self._data

    def GetDifferentiaVals(
        self: "HereditaryStratigraphicSpecimen",
    ) -> np.ndarray:
        """Get the integer underlying values in the stored Pandas Series.

        Returns
        -------
        differentia : np.ndarray
            A 1-dimensional NumPy integer ndarray containing differentia values,
            including garbage values where the underlying Series is null.

        Notes
        -----
        This function returns a direct view into the Series data, so no copy is
        made. Changes to the returned array will propagate to the Series
        object's underlying values, and vice versa.
        """
        return self._data.array.to_numpy(copy=False)

    def GetRankIndex(
        self: "HereditaryStratigraphicSpecimen",
    ) -> np.ndarray:
        """Get the integer index in the stored Pandas Series, representing the
        ranks of stratum entries.

        Returns
        -------
        ranks : np.ndarray
            A numpy array containing ranks of differentia entries, including
            null entries for differentia that are not retained.
        """
        return self._data.index.array.to_numpy(copy=False, dtype=np.uint64)

    def GetRankAtColumnIndex(
        self: "HereditaryStratigraphicSpecimen",
        index: int,
    ) -> int:
        """Map array position to generation of deposition.

        What is the deposition rank of the stratum positioned at index i
        among retained strata? Index order is from most ancient (index 0) to
        most recent.
        """
        return self.GetRankIndex()[index]

    def IterRetainedRanks(
        self: "HereditaryStratigraphicSpecimen",
    ) -> typing.Iterator[int]:
        """Iterate over deposition ranks of strata retained in the specimen."""
        yield from self.GetRankIndex()

    def IterRetainedDifferentia(
        self: "HereditaryStratigraphicSpecimen",
    ) -> typing.Iterator[int]:
        """Iterate over differentia of strata retained in the specimen.

        Differentia yielded from most ancient to most recent.
        """
        yield from self.GetDifferentiaVals()

    def IterRankDifferentiaZip(
        self: "HereditaryStratigraphicSpecimen",
        copyable: bool = False,
    ) -> typing.Iterator[typing.Tuple[int, int]]:
        """Iterate over ranks of retained strata and their differentia.

        If `copyable`, return an iterator that can be copied to produce a new
        fully-independent iterator at the same position.

        Equivalent to `zip(specimen.IterRetainedRanks(),
        specimen.IterRetainedDifferentia())`, but may be more efficient.
        """
        if copyable:
            return CopyableSeriesItemsIter(self._data)
        else:
            return self._data.items()
