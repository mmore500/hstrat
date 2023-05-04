from copy import copy
import operator
import typing

from interval_search import binary_search

from .._HereditaryStratum import HereditaryStratum
from ._detail import HereditaryStratumOrderedStoreBase


class HereditaryStratumOrderedStoreList(HereditaryStratumOrderedStoreBase):
    """Interchangeable backing container for HereditaryStratigraphicColumn.

    Stores deposited strata using a list implementation. Retained strata are
    stored from most ancient (index 0, front) to most recent (back). Cloned
    stores instantiate an independent list (although strata are not deepcopied
    themselves).

    Potentially useful in scenarios where moderate strata counts are retained,
    many strata are deposited without column cloning, deleted strata tend to
    be more recent (i.e., not more ancient and toward the front of the list),
    or many comparisons to estimate most recent common ancestor are made
    between stratigraphic columns.
    """

    __slots__ = ("_data",)

    # strata stored from most ancient (index 0, front) to most recent (back)
    _data: typing.List[HereditaryStratum]

    def __init__(self: "HereditaryStratumOrderedStoreList"):
        """Initialize instance variables."""
        self._data = []

    def __eq__(
        self: "HereditaryStratumOrderedStoreList",
        other: "HereditaryStratumOrderedStoreList",
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

    def DepositStratum(
        self: "HereditaryStratumOrderedStoreList",
        rank: typing.Optional[int],
        stratum: "HereditaryStratum",
    ) -> None:
        """Insert a new stratum into the store.

        Parameters
        ----------
        rank : typing.Optional[int]
            The position of the stratum being deposited within the sequence of strata deposited into the column. Precisely, the number of strata that have been deposited before stratum.
        stratum : HereditaryStratum
            The stratum to deposit.
        """
        self._data.append(stratum)

    def GetNumStrataRetained(self: "HereditaryStratumOrderedStoreList") -> int:
        """How many strata are present in the store?

        May be fewer than the number of strata deposited if deletions have
        occured.
        """
        return len(self._data)

    def GetStratumAtColumnIndex(
        self: "HereditaryStratumOrderedStoreList",
        index: int,
        # needed for other implementations
        get_rank_at_column_index: typing.Optional[typing.Callable] = None,
    ) -> HereditaryStratum:
        """Get the stratum positioned at index i among retained strata.

        Index order is from most ancient (index 0) to most recent.

        Parameters
        ----------
        ranks : iterator over int
            The ranks that to be deleted.
        get_column_index_of_rank : callable, optional
            Callable that returns the index position within retained strata of
            the stratum deposited at rank r.
        """
        return self._data[index]

    def GetRankAtColumnIndex(
        self: "HereditaryStratumOrderedStoreList",
        index: int,
    ) -> int:
        """Map from deposition generation to column position.

        What is the deposition rank of the stratum positioned at index i
        among retained strata? Index order is from most ancient (index 0) to
        most recent.
        """
        res_rank = self.GetStratumAtColumnIndex(index).GetDepositionRank()
        assert res_rank is not None
        return res_rank

    def GetColumnIndexOfRank(
        self: "HereditaryStratumOrderedStoreList",
        rank: int,
    ) -> typing.Optional[int]:
        """Map from column position to deposition generation

        What is the index position within retained strata of the stratum
        deposited at rank r? Returns None if no stratum with rank r is present
        within the store.
        """
        if self.GetNumStrataRetained() == 0:
            return None
        else:
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

    def DelRanks(
        self: "HereditaryStratumOrderedStoreList",
        ranks: typing.Iterator[int],
        # deposition ranks might not be stored in strata
        get_column_index_of_rank: typing.Optional[typing.Callable] = None,
    ) -> None:
        """Purge strata with specified deposition ranks from the store.

        Parameters
        ----------
        ranks : iterator over int
            The ranks that to be deleted.
        get_column_index_of_rank : callable, optional
            Callable that returns the deposition rank of the stratum positioned
            at index i among retained strata.
        """
        if get_column_index_of_rank is None:
            get_column_index_of_rank = self.GetColumnIndexOfRank

        indices = [get_column_index_of_rank(rank) for rank in ranks]
        # adapted from https://stackoverflow.com/a/11303234/17332200
        # iterate over indices in reverse order to prevent invalidation
        # reversed() is an potential optimization
        # given indices is assumed to be in ascending order
        for index in sorted(reversed(indices), reverse=True):
            assert index is not None
            del self._data[index]

    def IterRetainedRanks(
        self: "HereditaryStratumOrderedStoreList",
    ) -> typing.Iterator[int]:
        """Iterate over deposition ranks of strata present in the store from
        most ancient to most recent.

        The store may be altered during iteration without iterator
        invalidation, although subsequent updates will not be reflected in the
        iterator.
        """
        # must make copy to prevent invalidation when strata are deleted
        # note, however, that copy is made lazily
        # (only when first item requested)
        ranks = [stratum.GetDepositionRank() for stratum in self._data]
        for rank in ranks:
            assert rank is not None
            yield rank

    def IterRetainedStrata(
        self: "HereditaryStratumOrderedStoreList",
    ) -> typing.Iterator[HereditaryStratum]:
        """Iterate over stored strata from most ancient to most recent."""
        yield from self._data

    def IterRankDifferentiaZip(
        self: "HereditaryStratumOrderedStoreList",
        # deposition ranks might not be stored in strata
        get_rank_at_column_index: typing.Optional[typing.Callable] = None,
        start_column_index: int = 0,
    ) -> typing.Iterator[typing.Tuple[int, int]]:
        """Iterate over differentia and corresponding deposition ranks.

        Values yielded as tuples. Guaranteed ordered from most ancient to most
        recent.

        Parameters
        ----------
        get_rank_at_column_index : callable, optional
            Callable that returns the deposition rank of the stratum positioned
            at index i among retained strata.
        start_column_index : callable, optional
            Number of strata to skip over before yielding first result from the
            iterator. Default 0, meaning no strata are skipped over.
        """
        if get_rank_at_column_index is None:
            get_rank_at_column_index = self.GetRankAtColumnIndex

        # adapted from https://stackoverflow.com/a/12911454
        for index in range(start_column_index, len(self._data)):
            stratum = self._data[index]
            yield (get_rank_at_column_index(index), stratum.GetDifferentia())

    def Clone(
        self: "HereditaryStratumOrderedStoreList",
    ) -> "HereditaryStratumOrderedStoreList":
        """Create an independent copy of the store.

        Returned copy contains identical data but may be freely altered without
        affecting data within this store.
        """
        # shallow copy
        result = copy(self)
        # do semi-shallow clone on select elements
        # see https://stackoverflow.com/a/47859483 for performance consierations
        result._data = [*self._data]
        return result
