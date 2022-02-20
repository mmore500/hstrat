from bitarray import frozenbitarray
from copy import copy
import typing

from ..helpers import binary_search

from .HereditaryStratum import HereditaryStratum

class HereditaryStratumOrderedStoreList:

    _data: typing.List[HereditaryStratum]

    def __init__(self: 'HereditaryStratumOrderedStoreList'):
        self._data = []

    def __eq__(
        self: 'HereditaryStratumOrderedStoreList',
        other: 'HereditaryStratumOrderedStoreList',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def DepositStratum(
        self: 'HereditaryStratumOrderedStoreList',
        rank: int,
        stratum: 'HereditaryStratum',
    ) -> None:
        self._data.append(stratum)

    def GetNumStrataRetained(self: 'HereditaryStratumOrderedStoreList') -> int:
        return len(self._data)

    def GetStratumAtColumnIndex(
        self: 'HereditaryStratumOrderedStoreList',
        index: int,
        # needed for other implementations
        get_rank_at_column_index: typing.Optional[typing.Callable]=None,
    ) -> HereditaryStratum:
        return self._data[index]

    def GetRankAtColumnIndex(
        self: 'HereditaryStratumOrderedStoreList',
        index: int,
    ) -> int:
        res_rank = self.GetStratumAtColumnIndex(index).GetDepositionRank()
        assert res_rank is not None
        return res_rank

    def GetColumnIndexOfRank(
        self: 'HereditaryStratumOrderedStoreList',
        rank: int,
    ) -> typing.Optional[int]:
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
        self: 'HereditaryStratumOrderedStoreList',
        ranks: typing.Iterator[int],
        # deposition ranks might not be stored in strata
        get_column_index_of_rank: typing.Optional[typing.Callable]=None,
    ) -> None:
        if get_column_index_of_rank is None:
            get_column_index_of_rank = self.GetColumnIndexOfRank

        indices = [
            get_column_index_of_rank(rank)
            for rank in ranks
        ]
        # adapted from https://stackoverflow.com/a/11303234/17332200
        # iterate over indices in reverse order to prevent invalidation
        # reversed() is an potential optimization
        # given indices is assumed to be in ascending order
        for index in sorted(reversed(indices), reverse=True):
            assert index is not None
            del self._data[index]

    def GetRetainedRanks(
        self: 'HereditaryStratumOrderedStoreDict',
    ) -> typing.Iterator[int]:
        # must make copy to prevent invalidation when strata are deleted
        # note, however, that copy is made lazily
        # (only when first item requested)
        ranks = [
            stratum.GetDepositionRank()
            for stratum in self._data
        ]
        for rank in ranks:
            assert rank is not None
            yield rank

    def IterRankUid(
        self: 'HereditaryStratumOrderedStoreList',
        # deposition ranks might not be stored in strata
        get_rank_at_column_index: typing.Optional[typing.Callable]=None,
        start_column_index: int=0,
    ) -> typing.Iterator[typing.Tuple[int, frozenbitarray]]:
        if get_rank_at_column_index is None:
            get_rank_at_column_index = self.GetRankAtColumnIndex

        # adapted from https://stackoverflow.com/a/12911454
        for index in range(start_column_index, len(self._data)):
            stratum = self._data[index]
            yield (get_rank_at_column_index(index), stratum.GetUid())

    def Clone(
            self: 'HereditaryStratumOrderedStoreList',
    ) -> 'HereditaryStratumOrderedStoreList':
        # shallow copy
        result = copy(self)
        # do semi-shallow clone on select elements
        # see https://stackoverflow.com/a/47859483 for performance consierations
        result._data = [*self._data]
        return result
