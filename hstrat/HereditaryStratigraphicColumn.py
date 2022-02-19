from copy import deepcopy
from iterpop import iterpop as ip
import itertools as it
import math
import operator
import typing

from ..helpers import binary_search
from ..helpers import value_or

from .HereditaryStratum import HereditaryStratum
from .HereditaryStratumOrderedStoreList import HereditaryStratumOrderedStoreList

from .stratum_retention_condemners import StratumRetentionCondemnerFromPredicate
from .stratum_retention_condemners import StratumRetentionCondemnerMaximal


class HereditaryStratigraphicColumn:

    _stratum_ordered_store: typing.Any
    _num_strata_deposited: int
    _default_stratum_uid_size: int
    _stratum_retention_condemner: typing.Callable

    def __init__(
        self: 'HereditaryStratigraphicColumn',
        *,
        initial_stratum_annotation: typing.Optional[typing.Any]=None,
        default_stratum_uid_size: int=64,
        stratum_retention_condemner: typing.Callable=None,
        stratum_retention_predicate: typing.Callable=None,
        stratum_ordered_store_factory: typing.Callable
            =HereditaryStratumOrderedStoreList,
    ):
        """
        Retention predicate should take two keyword arguments: stratum_rank and column_strata_deposited.
        Default retention predicate is to keep all strata."""
        self._stratum_ordered_store = stratum_ordered_store_factory()
        self._num_strata_deposited = 0
        self._default_stratum_uid_size = default_stratum_uid_size

        if None not in (
            stratum_retention_predicate,
            stratum_retention_condemner,
        ):
            raise ValueError(
                'Exactly one of `stratum_retention_condemner` '
                'and `stratum_retention_predicate` must be provided.'
            )
        else:
            self._stratum_retention_condemner = (
                StratumRetentionCondemnerFromPredicate(
                    stratum_retention_predicate,
                )
                    if (stratum_retention_predicate is not None)
                else stratum_retention_condemner
                    if stratum_retention_condemner is not None
                else StratumRetentionCondemnerMaximal()
            )

        self.DepositStratum(annotation=initial_stratum_annotation)

    def __eq__(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def HasClosedFormRankAtColumnIndex(
        self: 'HereditaryStratigraphicColumn',
    ) -> bool:
        return hasattr(
            self._stratum_retention_condemner,
            'CalcRankAtColumnIndex',
        )

    def DepositStratum(
        self: 'HereditaryStratigraphicColumn',
        annotation: typing.Optional[typing.Any]=None,
    ) -> None:

        new_stratum = HereditaryStratum(
            annotation=annotation,
            deposition_rank=(
                # don't store deposition rank if we know how to calcualte it
                # from stratum's position in column
                None
                if self.HasClosedFormRankAtColumnIndex()
                else self._num_strata_deposited
            ),
            uid_size=self._default_stratum_uid_size,
        )
        self._stratum_ordered_store.DepositStratum(
            rank=self._num_strata_deposited,
            stratum=new_stratum,
        )
        self._PurgeColumn()
        self._num_strata_deposited += 1

    def _PurgeColumn(self: 'HereditaryStratigraphicColumn') -> None:
        condemned_ranks = self._stratum_retention_condemner(
            retained_ranks=self.GetRetainedRanks(),
            num_strata_deposited=self.GetNumStrataDeposited(),
        )
        self._stratum_ordered_store.DelRanks(
            ranks=condemned_ranks,
            get_column_index_of_rank=self.GetColumnIndexOfRank,
        )

    def GetRetainedRanks(
        self: 'HereditaryStratigraphicColumn',
    ) -> typing.Iterator[int]:
            if self.HasClosedFormRankAtColumnIndex():
                for idx in range(self.GetNumStrataRetained()):
                    yield self.GetRankAtColumnIndex(idx)
            else:
                yield from self._stratum_ordered_store.GetRetainedRanks()

    def GetNumStrataRetained(self: 'HereditaryStratigraphicColumn') -> int:
        return self._stratum_ordered_store.GetNumStrataRetained()

    def GetNumStrataDeposited(self: 'HereditaryStratigraphicColumn') -> int:
        return self._num_strata_deposited

    def GetStratumAtColumnIndex(
        self: 'HereditaryStratigraphicColumn',
        index: int,
    ) -> HereditaryStratum:
        return self._stratum_ordered_store.GetStratumAtColumnIndex(
            index,
            get_rank_at_column_index=(
                self.GetRankAtColumnIndex
                if self.HasClosedFormRankAtColumnIndex()
                else None
            ),
        )

    def GetRankAtColumnIndex(
        self: 'HereditaryStratigraphicColumn',
        index: int,
    ) -> int:
        if self.HasClosedFormRankAtColumnIndex():
            return self._stratum_retention_condemner.CalcRankAtColumnIndex(
                index=index,
                num_strata_deposited=self.GetNumStrataDeposited(),
            )
        else:
            # fall back to store lookup
            return self._stratum_ordered_store.GetRankAtColumnIndex(index)

    def GetColumnIndexOfRank(
        self: 'HereditaryStratumOrderedStoreList',
        rank: int,
    ) -> typing.Optional[int]:
        if self.HasClosedFormRankAtColumnIndex():
            assert self.GetNumStrataRetained()
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
        else:
            # fall back to store lookup
            return self._stratum_ordered_store.GetColumnIndexOfRank(rank=rank)

    def GetNumDiscardedStrata(
        self: 'HereditaryStratigraphicColumn',
    ) -> int:
        return self.GetNumStrataDeposited() - self.GetNumStrataRetained()

    def HasDiscardedStrata(
        self: 'HereditaryStratigraphicColumn',
    ) -> bool:
        return self.GetNumDiscardedStrata() > 0

    def CalcRankOfLastCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        if self.HasDiscardedStrata() or other.HasDiscardedStrata():
            return self._do_generic_CalcRankOfLastCommonalityWith(other)
        else:
            return self._do_binary_search_CalcRankOfLastCommonalityWith(other)

    def _do_binary_search_CalcRankOfLastCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        """Assumes both self and other use the maximal retention predicate."""

        assert not self.HasDiscardedStrata() and not other.HasDiscardedStrata()

        lower_bound = 0
        upper_bound = min([
            self.GetNumStrataDeposited() - 1,
            other.GetNumStrataDeposited() - 1,
        ])
        assert lower_bound <= upper_bound
        rank_at = lambda which, idx: which.GetRankAtColumnIndex(idx)
        uid_at = lambda which, idx: which.GetStratumAtColumnIndex(idx).GetUid()
        predicate = lambda idx: uid_at(self, idx) != uid_at(other, idx)

        first_disparite_idx = binary_search(
            predicate,
            lower_bound,
            upper_bound,
        )

        if first_disparite_idx is None:
            # no disparate strata found
            # fallback to _do_generic_CalcRankOfLastCommonalityWith to handle
            # proper bookkeeping in this case while skipping most of the search
            return self._do_generic_CalcRankOfLastCommonalityWith(
                other,
                self_start_idx=upper_bound,
                other_start_idx=upper_bound,
            )
        elif first_disparite_idx > 0:
            # disparate strata found, following some common strata
            last_common_idx = first_disparite_idx - 1
            last_common_rank = self.GetRankAtColumnIndex(
                last_common_idx,
            )
            return last_common_rank
        else:
            # no common strata between self and other
            return None

    def _do_generic_CalcRankOfLastCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        *,
        self_start_idx: int=0,
        other_start_idx: int=0,
    ) -> typing.Optional[int]:
        # helper setup
        self_iter = self._stratum_ordered_store.IterRankUid(
            get_rank_at_column_index=self.GetRankAtColumnIndex,
            start_column_index=self_start_idx,
        )
        other_iter = other._stratum_ordered_store.IterRankUid(
            get_rank_at_column_index=other.GetRankAtColumnIndex,
            start_column_index=other_start_idx,
        )
        self_cur_rank, self_cur_uid = next(self_iter)
        other_cur_rank, other_cur_uid = next(other_iter)

        last_common_rank = None
        # a.k.a.
        # while (
        #     self_column_idx < self.GetNumStrataRetained()
        #     and other_column_idx < other.GetNumStrataRetained()
        # ):
        try:
            while True:
                if (self_cur_rank == other_cur_rank):
                    # strata at same rank can be compared
                    if (self_cur_uid == other_cur_uid):
                        # matching uids at the same rank,
                        # store rank and keep searching for mismatch
                        last_common_rank = self_cur_rank
                        # advance self
                        self_cur_rank, self_cur_uid = next(self_iter)
                        # advance other
                        other_cur_rank, other_cur_uid = next(other_iter)
                    else:
                        # mismatching uids at the same rank
                        # a.k.a. break
                        raise StopIteration
                elif self_cur_rank < other_cur_rank:
                    # current stratum on self column older than on other column
                    # advance to next-newer stratum on self column
                    self_cur_rank, self_cur_uid = next(self_iter)
                elif self_cur_rank > other_cur_rank:
                    # current stratum on other column older than on self column
                    # advance to next-newer stratum on other column
                    other_cur_rank, other_cur_uid = next(other_iter)
        except StopIteration:
            return last_common_rank

    def CalcRankOfFirstDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        if self.HasDiscardedStrata() or other.HasDiscardedStrata():
            return self._do_generic_CalcRankOfFirstDisparityWith(other)
        else:
            return self._do_binary_search_CalcRankOfFirstDisparityWith(other)

    def _do_binary_search_CalcRankOfFirstDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        """Assumes both self and other use the maximal retention predicate."""

        assert not self.HasDiscardedStrata() and not other.HasDiscardedStrata()

        lower_bound = 0
        upper_bound = min([
            self.GetNumStrataDeposited() - 1,
            other.GetNumStrataDeposited() - 1,
        ])
        assert lower_bound <= upper_bound
        rank_at = lambda which, idx: which.GetRankAtColumnIndex(idx)
        uid_at = lambda which, idx: which.GetStratumAtColumnIndex(idx).GetUid()
        predicate = lambda idx: uid_at(self, idx) != uid_at(other, idx)

        first_disparite_idx = binary_search(
            predicate,
            lower_bound,
            upper_bound,
        )

        if first_disparite_idx is not None:
            # disparate strata found
            first_disparite_rank = self.GetRankAtColumnIndex(
                first_disparite_idx,
            )
            return first_disparite_rank
        else:
            # no disparate strata found
            # fallback to _do_generic_CalcRankOfFirstDisparityWith to handle
            # proper bookkeeping in this case while skipping most of the search
            return self._do_generic_CalcRankOfFirstDisparityWith(
                other,
                self_start_idx=upper_bound,
                other_start_idx=upper_bound,
            )


    def _do_generic_CalcRankOfFirstDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
        *,
        self_start_idx: int=0,
        other_start_idx: int=0,
    ) -> typing.Optional[int]:
        self_column_idx = self_start_idx
        other_column_idx = other_start_idx

        # helper lambdas
        rank_at = lambda which, idx: which.GetRankAtColumnIndex(idx)
        uid_at = lambda which, idx: which.GetStratumAtColumnIndex(idx).GetUid()
        column_idxs_bounds_check = lambda: (
            self_column_idx < self.GetNumStrataRetained()
            and other_column_idx < other.GetNumStrataRetained()
        )

        while column_idxs_bounds_check():
            if (
                rank_at(self, self_column_idx)
                == rank_at(other, other_column_idx)
            ):
                # strata at same rank can be compared
                if (
                    uid_at(self, self_column_idx)
                    == uid_at(other, other_column_idx)
                ):
                    # matching uids at the same rank,
                    # keep searching for mismatch
                    self_column_idx += 1
                    other_column_idx += 1
                else:
                    # mismatching uids at the same rank
                    res = rank_at(self, self_column_idx)
                    assert 0 <= res < self.GetNumStrataDeposited()
                    return res
            elif (
                rank_at(self, self_column_idx)
                < rank_at(other, other_column_idx)
            ):
                # current stratum on self column older than on other column
                # advance to next-newer stratum on self column
                self_column_idx += 1
            elif (
                rank_at(self, self_column_idx)
                > rank_at(other, other_column_idx)
            ):
                # current stratum on other column older than on self column
                # advance to next-newer stratum on other column
                other_column_idx += 1

        if self_column_idx < self.GetNumStrataRetained():
            # although no mismatching strata are found between self and other
            # self has strata ranks beyond the newest found in other
            # conservatively assume mismatch will be with next rank of other
            assert other_column_idx == other.GetNumStrataRetained()
            res = rank_at(other, other_column_idx - 1) + 1
            assert 0 <= res <= self.GetNumStrataDeposited()
            return res
        elif other_column_idx < other.GetNumStrataRetained():
            # although no mismatching strata are found between other and self
            # other has strata ranks beyond the newest found in self
            # conservatively assume mismatch will be with next rank
            assert self_column_idx == self.GetNumStrataRetained()
            res = rank_at(self, self_column_idx - 1) + 1
            assert 0 <= res <= self.GetNumStrataDeposited()
            return res
        else:
            # no disparate strata found
            # and self and other have the same newest rank
            return None

    def CalcRankOfMrcaBoundsWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[typing.Tuple[int, int]]:
        if self.HasAnyCommonAncestorWith(other):
            first_disparity = self.CalcRankOfFirstDisparityWith(other)
            if first_disparity is None:
                num_self_deposited = self.GetNumStrataDeposited()
                num_other_deposited = other.GetNumStrataDeposited()
                assert num_self_deposited == num_other_deposited
            return (
                self.CalcRankOfLastCommonalityWith(other),
                value_or(first_disparity, self.GetNumStrataDeposited()),
            )
        else: return None

    def CalcRankOfMrcaUncertaintyWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> int:
        bounds = self.CalcRankOfMrcaBoundsWith(other)
        return 0 if bounds is None else abs(operator.sub(*bounds)) - 1

    def CalcRanksSinceLastCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        last_common_rank = self.CalcRankOfLastCommonalityWith(other,)
        if last_common_rank is None: return None
        else:
            assert self.GetNumStrataDeposited()
            res = self.GetNumStrataDeposited() - 1 - last_common_rank
            assert 0 <= res < self.GetNumStrataDeposited()
            return res

    # note, returns -1 if disparity is that other has advanced to ranks
    # past self's largest rank
    def CalcRanksSinceFirstDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        first_disparate_rank = self.CalcRankOfFirstDisparityWith(other,)
        if first_disparate_rank is None: return None
        else:
            assert self.GetNumStrataDeposited()
            res = self.GetNumStrataDeposited() - 1 - first_disparate_rank
            assert -1 <= res < self.GetNumStrataDeposited()
            return res

    def CalcRanksSinceMrcaBoundsWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[typing.Tuple[int, int]]:
        if self.HasAnyCommonAncestorWith(other):
            since_first_disparity = self.CalcRanksSinceFirstDisparityWith(other)
            lb_exclusive = value_or(since_first_disparity, -1)
            lb_inclusive = lb_exclusive + 1

            since_last_common = self.CalcRanksSinceLastCommonalityWith(other)
            ub_inclusive = since_last_common
            ub_exclusive = ub_inclusive + 1

            return (lb_inclusive, ub_exclusive)
        else:
            return None

    def CalcRanksSinceMrcaUncertaintyWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> int:
        bounds = self.CalcRanksSinceMrcaBoundsWith(other)
        return 0 if bounds is None else abs(operator.sub(*bounds)) - 1

    def GetLastCommonStratumWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[HereditaryStratum]:
        rank = self.CalcRankOfLastCommonalityWith(other)
        if rank is not None:
            index = ip.popsingleton(
                index
                for index in range(self.GetNumStrataRetained())
                if rank == self.GetRankAtColumnIndex(index)
            )
            return self.GetStratumAtColumnIndex(index)
        else: return None

    def HasAnyCommonAncestorWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> bool:
        first_disparity = self.CalcRankOfFirstDisparityWith(other)
        return True if first_disparity is None else first_disparity > 0

    def MakeDescendantColumn(
        self: 'HereditaryStratigraphicColumn',
        stratum_annotation: typing.Optional[typing.Any]=None,
    ) -> 'HereditaryStratigraphicColumn':
        res = deepcopy(self)
        res.DepositStratum(annotation=stratum_annotation)
        return res
