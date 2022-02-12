import operator
import math
import typing

from .HereditaryStratum import HereditaryStratum
from .StratumRetentionPredicateMaximal import StratumRetentionPredicateMaximal


class HereditaryStratigraphicColumn:

    _column: typing.List[HereditaryStratum,]
    _num_strata_deposited: int
    _default_stratum_uid_size: int
    _stratum_retention_predicate: typing.Callable[[int, int], bool]

    def __init__(
        self: 'HereditaryStratigraphicColumn',
        *,
        default_stratum_uid_size: int=64,
        stratum_retention_predicate=StratumRetentionPredicateMaximal(),
    ):
        """
        Retention predicate should take two keyword arguments: stratum_rank and column_strata_deposited.
        Default retention predicate is to keep all strata."""
        self._column = []
        self._num_strata_deposited = 0
        self._default_stratum_uid_size = default_stratum_uid_size
        self._stratum_retention_predicate = stratum_retention_predicate

        self.DepositStratum()

    def __eq__(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def DepositStratum(self: 'HereditaryStratigraphicColumn',) -> None:
        self._column.append(HereditaryStratum(
            deposition_rank=(
                None
                if hasattr(
                    self._stratum_retention_predicate,
                    'CalcRankAtColumnIndex',
                ) else self._num_strata_deposited
            ),
            uid_size=self._default_stratum_uid_size,
        ))
        self._PurgeColumn()
        self._num_strata_deposited += 1

    def _PurgeColumn(self: 'HereditaryStratigraphicColumn',) -> None:
        # wrapper to enforce requirements on predicate
        def should_retain(stratum_rank: int,) -> bool:
            res = self._stratum_retention_predicate(
                stratum_rank=stratum_rank,
                column_strata_deposited=self.GetNumStrataDeposited(),
            )
            # predicate must *always* retain the initial and latest strata
            if stratum_rank in (0, self.GetNumStrataDeposited()):
                assert res
            return res

        self._column = [
            entry
            for idx, entry in enumerate(self._column)
            if should_retain(self.CalcRankAtColumnIndex(idx))
        ]

    def GetNumStrataRetained(self: 'HereditaryStratigraphicColumn',) -> int:
        return len(self._column)

    def GetNumStrataDeposited(self: 'HereditaryStratigraphicColumn',) -> int:
        return self._num_strata_deposited

    def CalcRankAtColumnIndex(
        self: 'HereditaryStratigraphicColumn',
        index: int,
    ) -> int:
        maybe_rank = self._column[index].GetDepositionRank()
        if maybe_rank is not None:
            return maybe_rank
        else:
            return self._stratum_retention_predicate.CalcRankAtColumnIndex(
                index=index,
                num_strata_deposited=self.GetNumStrataDeposited(),
            )

    def CalcRankOfLastCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        self_column_idx = 0
        other_column_idx = 0
        last_common_rank = None

        # helper lambdas
        rank_at = lambda which, idx: which.CalcRankAtColumnIndex(idx)
        uid_at = lambda which, idx: which._column[idx].GetUid()

        while (
            self_column_idx < self.GetNumStrataRetained()
            and other_column_idx < other.GetNumStrataRetained()
        ):
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
                    # store rank and keep searching for mismatch
                    last_common_rank = rank_at(self, self_column_idx)
                    self_column_idx += 1
                    other_column_idx += 1
                else:
                    # mismatching uids at the same rank
                    break
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

        return last_common_rank

    def CalcRankOfFirstDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:
        self_column_idx = 0
        other_column_idx = 0
        last_common_rank = None

        # helper lambdas
        rank_at = lambda which, idx: which.CalcRankAtColumnIndex(idx)
        uid_at = lambda which, idx: which._column[idx].GetUid()
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
    ) -> typing.Tuple[typing.Optional[int], typing.Optional[int]]:
        return (
            self.CalcRankOfLastCommonalityWith(other),
            self.CalcRankOfFirstDisparityWith(other),
        )

    def CalcRankOfMrcaUncertaintyWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) :
        bounds = self.CalcRankOfMrcaBoundsWith(other)
        if None in bounds: return 0
        else: return abs(operator.sub(*bounds)) - 1

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
    ) -> typing.Tuple[typing.Optional[int], typing.Optional[int],]:
        return (
            self.CalcRanksSinceLastCommonalityWith(other,),
            self.CalcRanksSinceFirstDisparityWith(other,),
        )

    def CalcRanksSinceMrcaUncertaintyWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) :
        bounds = self.CalcRanksSinceMrcaBoundsWith(other)
        if None in bounds: return 0
        else: return abs(operator.sub(*bounds)) - 1
