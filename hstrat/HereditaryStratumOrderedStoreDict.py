from copy import copy
import itertools as it
import sys
import typing

from .HereditaryStratum import HereditaryStratum


class HereditaryStratumOrderedStoreDict:

    # maps rank to stratum
    _data: typing.Dict[int, HereditaryStratum]

    def __init__(self: 'HereditaryStratumOrderedStoreDict'):
        self._data = {}

    def __eq__(
        self: 'HereditaryStratumOrderedStoreDict',
        other: 'HereditaryStratumOrderedStoreDict',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def DepositStratum(
        self: 'HereditaryStratumOrderedStoreDict',
        rank: int,
        stratum: 'HereditaryStratum',
    ) -> None:
        self._data[rank] = stratum

    def GetNumStrataRetained(self: 'HereditaryStratumOrderedStoreDict') -> int:
        return len(self._data)

    def GetStratumAtColumnIndex(
        self: 'HereditaryStratumOrderedStoreDict',
        index: int,
        get_rank_at_column_index: typing.Optional[typing.Callable]=None,
    ) -> HereditaryStratum:
        if get_rank_at_column_index is not None:
            return self._data[get_rank_at_column_index(index)]
        else:
            # for python 3.7+, dictionaries are guaranteed insertion ordered
            assert sys.version_info >= (3, 7)
            return next(it.islice(self._data.values(), index, None))

    def GetRankAtColumnIndex(
        self: 'HereditaryStratumOrderedStoreDict',
        index: int,
    ) -> int:
        # for python 3.7+, dictionaries are guaranteed insertion ordered
        assert sys.version_info >= (3, 7)
        return next(it.islice(self._data.keys(), index, None))

    def GetColumnIndexOfRank(
        self: 'HereditaryStratumOrderedStoreDict',
        rank: int,
    ) -> typing.Optional[int]:
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
        self: 'HereditaryStratumOrderedStoreDict',
        ranks: typing.Iterable[int],
        # needed for other implementations
        get_column_index_of_rank: typing.Optional[typing.Callable]=None,
    ) -> None:
        for rank in ranks:
            del self._data[rank]

    def GetRetainedRanks(
        self: 'HereditaryStratumOrderedStoreDict',
    ) -> typing.Iterator[int]:
        # must make copy to prevent
        # `RuntimeError: dictionary changed size during iteration`
        # note, however, that copy is made lazily
        # (only when first item requested)
        yield from list(self._data.keys())

    def IterRankUid(
        self: 'HereditaryStratumOrderedStoreDict',
        # needed for other implementations
        get_rank_at_column_index: typing.Optional[typing.Callable]=None,
        start_column_index: int=0,
    ) -> typing.Iterator[typing.Tuple[int, int]]:
        # optimization idea:
        # python dicts are ordered, so is there a way to begin iterating
        # from a specified item in the dict?
        # current method must iterate past skipped over items
        # adapted from https://stackoverflow.com/a/12911454
        iter_ = it.islice(self._data.items(), start_column_index, None)
        for rank, stratum in iter_:
            yield (rank, stratum.GetUid())

    def Clone(
            self: 'HereditaryStratumOrderedStoreDict',
    ) -> 'HereditaryStratumOrderedStoreDict':
        # shallow copy
        result = copy(self)
        # do semi-shallow clone on select elements
        # see https://stackoverflow.com/a/5861653 for performance consierations
        result._data = self._data.copy()
        return result
