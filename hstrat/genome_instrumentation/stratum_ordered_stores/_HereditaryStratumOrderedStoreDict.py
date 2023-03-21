from copy import copy
import itertools as it
import operator
import sys
import typing

from .._HereditaryStratum import HereditaryStratum
from ._detail import HereditaryStratumOrderedStoreBase


class HereditaryStratumOrderedStoreDict(HereditaryStratumOrderedStoreBase):
    """Interchangeable backing container for HereditaryStratigraphicColumn.

    Stores deposited strata using a dict implementation. Retained strata are
    stored as dict values with their associated deposition ranks as keys.

    Potentially useful in scenarios where large strata counts are retained or
    deleted strata tend to be more ancient.
    """

    __slots__ = ("_data",)

    # maps rank to stratum
    _data: typing.Dict[int, HereditaryStratum]

    def __init__(self: "HereditaryStratumOrderedStoreDict"):
        """Initialize instance variables."""
        self._data = {}

    def __eq__(
        self: "HereditaryStratumOrderedStoreDict",
        other: "HereditaryStratumOrderedStoreDict",
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
        self: "HereditaryStratumOrderedStoreDict",
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
        self._data[rank] = stratum

    def GetNumStrataRetained(self: "HereditaryStratumOrderedStoreDict") -> int:
        """How many strata are present in the store?

        May be fewer than the number of strata deposited if deletions have
        occured.
        """
        return len(self._data)

    def GetStratumAtColumnIndex(
        self: "HereditaryStratumOrderedStoreDict",
        index: int,
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
        if get_rank_at_column_index is not None:
            return self._data[get_rank_at_column_index(index)]
        else:
            # for python 3.7+, dictionaries are guaranteed insertion ordered
            assert sys.version_info >= (3, 7)
            return next(it.islice(self._data.values(), index, None))

    def GetRankAtColumnIndex(
        self: "HereditaryStratumOrderedStoreDict",
        index: int,
    ) -> int:
        """Map deposition generation to column position.

        What is the deposition rank of the stratum positioned at index i
        among retained strata? Index order is from most ancient (index 0) to
        most recent.
        """
        # for python 3.7+, dictionaries are guaranteed insertion ordered
        assert sys.version_info >= (3, 7)
        return next(it.islice(self._data.keys(), index, None))

    def GetColumnIndexOfRank(
        self: "HereditaryStratumOrderedStoreDict",
        rank: int,
    ) -> typing.Optional[int]:
        """Map column position ot deposition generation.

        What is the index position within retained strata of the stratum
        deposited at rank r? Returns None if no stratum with rank r is present
        within the store.
        """
        # for python 3.7+, dictionaries are guaranteed insertion ordered
        assert sys.version_info >= (3, 7)
        try:
            return next(
                idx
                for idx, rank_ in enumerate(self._data.keys())
                if rank_ == rank
            )
        except StopIteration:
            return None

    def DelRanks(
        self: "HereditaryStratumOrderedStoreDict",
        ranks: typing.Iterable[int],
        # needed for other implementations
        get_column_index_of_rank: typing.Optional[typing.Callable] = None,
    ) -> None:
        """Purge strata with specified deposition ranks from the store.

        Parameters
        ----------
        ranks : iterator over int
            The ranks that to be deleted.
        get_column_index_of_rank : callable, optional
            Callable that returns the deposition rank of the stratum positioned
            at index i among retained strata. Not used in this method.
        """
        for rank in ranks:
            del self._data[rank]

    def IterRetainedRanks(
        self: "HereditaryStratumOrderedStoreDict",
    ) -> typing.Iterator[int]:
        """Iterate over deposition ranks of strata present in the store from
        most ancient to most recent.

        The store may be altered during iteration without iterator
        invalidation, although subsequent updates will not be reflected in the
        iterator.
        """
        # must make copy to prevent
        # `RuntimeError: dictionary changed size during iteration`
        # note, however, that copy is made lazily
        # (only when first item requested)
        yield from list(self._data.keys())

    def IterRetainedStrata(
        self: "HereditaryStratumOrderedStoreDict",
    ) -> typing.Iterator[HereditaryStratum]:
        """Iterate over stored strata from most ancient to most recent."""
        # for python 3.7+, dictionaries are guaranteed insertion ordered
        assert sys.version_info >= (3, 7)
        yield from self._data.values()

    def IterRankDifferentiaZip(
        self: "HereditaryStratumOrderedStoreDict",
        # needed for other implementations
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
        # optimization idea:
        # python dicts are ordered, so is there a way to begin iterating
        # from a specified item in the dict?
        # current method must iterate past skipped over items
        # adapted from https://stackoverflow.com/a/12911454
        iter_ = it.islice(self._data.items(), start_column_index, None)
        for rank, stratum in iter_:
            yield (rank, stratum.GetDifferentia())

    def Clone(
        self: "HereditaryStratumOrderedStoreDict",
    ) -> "HereditaryStratumOrderedStoreDict":
        """Create an independent copy of the store.

        Returned copy contains identical data but may be freely altered without
        affecting data within this store.
        """
        # shallow copy
        result = copy(self)
        # do semi-shallow clone on select elements
        # see https://stackoverflow.com/a/5861653 for performance consierations
        result._data = self._data.copy()
        return result
