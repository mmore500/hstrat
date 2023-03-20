import functools
import typing

import numpy as np
import pandera as pa

from .._auxiliary_lib import (
    CopyableSeriesItemsIter,
    get_nullable_mask,
    get_nullable_vals,
)

_nullable_unsigned_integer_series_t = typing.Union[
    pa.typing.Series[pa.typing.UINT8()],
    pa.typing.Series[pa.typing.UINT16()],
    pa.typing.Series[pa.typing.UINT32()],
    pa.typing.Series[pa.typing.UINT64()],
]


class HereditaryStratigraphicAssemblageSpecimen:
    """Postprocessing representation of the differentia retained by an extant
    HereditaryStratigraphicColumn, indexed by deposition rank.

    Differentia are stored using a nullable integer representation, which allows
    for inclusion of entries for all ranks retained by any specimen within the
    assemblage, even if that particualr rank is not retained by this specimen.
    This allows for more efficient comparisons between specimens, due to direct
    alignment.

    See Also
    --------
    HereditaryStratigraphicSpecimen
        Specimen representation that can contain only ranks retained by that
        specimen.
    HereditaryStratigraphicAssemblage
        Gathers a collection of `HereditaryStratigraphicSpecimen`s and
        facilitates creation of corresponding aligned `HereditaryStratigraphicAssemblageSpecimen`s.
    """

    __slots__ = ("_data", "_stratum_differentia_bit_width")

    _data: _nullable_unsigned_integer_series_t
    _stratum_differentia_bit_width: int

    def __init__(
        self: "HereditaryStratigraphicAssemblageSpecimen",
        stratum_differentia_series: _nullable_unsigned_integer_series_t,
        stratum_differentia_bit_width: int,
    ) -> None:
        """Initialize a HereditaryStratigraphicAssemblageSpecimen object with a
        (potentially sparse) sequence of rank-indexed differentia and a
        differentia bit width."""
        self._data = stratum_differentia_series
        self._stratum_differentia_bit_width = stratum_differentia_bit_width

    def GetStratumDifferentiaBitWidth(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> int:
        """How many bits wide are the differentia of strata?"""
        return self._stratum_differentia_bit_width

    @functools.lru_cache(maxsize=None)
    def GetNumStrataDeposited(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> int:
        """How many strata have been depostited on the column?

        Note that a first stratum is deposited on the column during
        initialization.
        """
        return self._data.last_valid_index() + 1

    @functools.lru_cache(maxsize=None)
    def GetNumStrataRetained(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> int:
        """How many strata are currently stored within the column?

        May be fewer than the number of strata deposited if strata have been
        discarded as part of the configured stratum retention policy.
        """
        return len(self._data) - self.GetStratumMask().sum()

    def GetNumDiscardedStrata(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> int:
        """How many deposited strata have been discarded?

        Determined by number of generations elapsed and the configured column
        retention policy.
        """
        return self.GetNumStrataDeposited() - self.GetNumStrataRetained()

    def HasDiscardedStrata(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> bool:
        """Have any deposited strata been discarded?"""
        return self.GetNumDiscardedStrata() > 0

    def GetData(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> _nullable_unsigned_integer_series_t:
        """Get the underlying Pandas Series containing differentia values
        indexed by rank.

        Notes
        -----
        This function directly returns the specimen's underlying Series
        data, so mutation of the returned object will alter or invalidate this
        specimen.
        """
        return self._data

    def GetStratumMask(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> np.ndarray:
        """Get a boolean mask indicating which entries in the stored Pandas
        NullableInteger Series are null.

        I.e., which ranks does this specimen not retain differentia at?

        Returns
        -------
        mask : np.ndarray
            A 1-dimensional boolean NumPy ndarray.

            True values indicate nullness.

        Notes
        -----
        This function returns the underlying boolean mask used by the stored
        Pandas Series object to represent null values. This mask is a direct
        view into the Series data, so no copy is made. Changes to the mask will
        propagate to the store Series object, and vice versa.
        """
        try:
            return get_nullable_mask(self._data)
        except AttributeError:  # object type (not nullable int) array
            return self._data.isna()

    def GetDifferentiaVals(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> np.ndarray:
        """Get the integer underlying values in the stored Pandas
        NullableInteger Series.

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
        try:
            return get_nullable_vals(self._data)
        except AttributeError:  # object type (not nullable int) array
            return self._data.array

    def GetRankIndex(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> np.ndarray:
        """Get the integer index in the stored Pandas Series, representing the
        ranks of stratum entries.

        Returns
        -------
        ranks : np.ndarray
            A numpy array containing ranks of differentia entries, including
            null entries for differentia that are not retained.
        """
        return self._data.index.array.to_numpy()

    def GetRankAtColumnIndex(
        self: "HereditaryStratigraphicAssemblageSpecimen",
        index: int,
    ) -> int:
        """Map array position to generation of deposition.

        What is the deposition rank of the stratum positioned at index i
        among retained strata? Index order is from most ancient (index 0) to
        most recent.
        """
        return self.GetData().dropna().index[index]

    def IterRetainedRanks(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> typing.Iterator[int]:
        """Iterate over deposition ranks of strata retained in the specimen."""
        yield from self.GetData().dropna().index

    def IterRetainedDifferentia(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> typing.Iterator[int]:
        """Iterate over differentia of strata retained in the specimen.

        Differentia yielded from most ancient to most recent.
        """
        yield from self.GetData().dropna()

    def IterRankDifferentiaZip(
        self: "HereditaryStratigraphicAssemblageSpecimen",
        copyable: bool = False,
    ) -> typing.Iterator[typing.Tuple[int, int]]:
        """Iterate over ranks of retained strata and their differentia.

        If `copyable`, return an iterator that can be copied to produce a new
        fully-independent iterator at the same position.

        Equivalent to `zip(specimen.IterRetainedRanks(),
        specimen.IterRetainedDifferentia())`, but may be more efficient.
        """
        if copyable:
            return CopyableSeriesItemsIter(self._data.dropna())
        else:
            return self._data.dropna().items()
