import typing

import pandas as pd


class CopyableSeriesItemsIter:
    """An iterator that returns (index, value) pairs from a Pandas series.

    Parameters
    ----------
    series : pd.Series
        The series to iterate over.

    Returns
    -------
    CopyableSeriesItemsIter
        An iterator object that returns (index, value) pairs from the series.

    Raises
    ------
    StopIteration
        If there are no more items in the series to iterate over.

    Examples
    --------
    >>> s = pd.Series([1, 2, 3], index=['a', 'b', 'c'])
    >>> c = CopyableSeriesItemsIter(s)
    >>> list(c)
    [('a', 1), ('b', 2), ('c', 3)]
    """

    _position: int
    _series: pd.Series

    def __init__(self: "CopyableSeriesItemsIter", series: pd.Series) -> None:
        """Initialize a new CopyableSeriesItemsIter instance.

        Parameters
        ----------
        series : pd.Series
            The series to iterate over.
        """
        self._series = series
        self._position = 0

    def __iter__(self: "CopyableSeriesItemsIter") -> "CopyableSeriesItemsIter":
        """Enable iterability.

        Returns
        -------
        CopyableSeriesItemsIter
            The iterator object itself.
        """
        return self

    def __next__(self: "CopyableSeriesItemsIter") -> typing.Tuple:
        """Return the next (index, value) pair from the series.

        Returns
        -------
        typing.Tuple
            A tuple containing the index label and value of the next item in
            the series.

        Raises
        ------
        StopIteration
            If there are no more items in the series to iterate over.
        """
        if self._position >= len(self._series):
            raise StopIteration

        self._position += 1
        return (
            self._series.index[self._position - 1],
            self._series.iloc[self._position - 1],
        )
