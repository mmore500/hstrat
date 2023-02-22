import typing

import numpy as np
import pandas as pd
import pandera as pa

from .._auxiliary_lib import (
    get_nullable_mask,
    get_nullable_vals,
    numpy_index_flat,
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
        """Initialize a HereditaryStratigraphicSpecimen object with a
        (potentially sparse) sequence of rank-indexed differentia and a
        differentia bit width."""
        self._data = stratum_differentia_series
        self._stratum_differentia_bit_width = stratum_differentia_bit_width

    def GetStratumDifferentiaBitWidth(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> int:
        """How many bits wide are the differentia of strata?"""
        return self._stratum_differentia_bit_width

    def GetNumStrataDeposited(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> int:
        """How many strata have been depostited on the column?

        Note that a first stratum is deposited on the column during
        initialization.
        """
        return self._data.last_valid_index() + 1

    def GetNumStrataRetained(
        self: "HereditaryStratigraphicAssemblageSpecimen",
    ) -> int:
        """How many strata are currently stored within the column?

        May be fewer than the number of strata deposited if strata have been
        discarded as part of the configured stratum retention policy.
        """
        return len(self._data) - self.GetStratumMask().sum()

    def GetData(
        self: "HereditaryStratigraphicSpecimen",
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
    ) -> pd.Index:
        """Get the integer index in the stored Pandas NullableInteger Series,
        representing the ranks of (possibly empty) stratum entries.

        Returns
        -------
        ranks : pd.Index
            A Pandas Index containing ranks of differentia entries, including
            null entries for differentia that are not retained.
        """
        return self._data.index
