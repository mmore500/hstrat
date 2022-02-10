import math
import typing

from . import HereditaryStratum

class HereditaryStratigraphicColumn:

    _column: typing.List[HereditaryStratum,]
    _num_layers_deposited: int
    _default_stratum_uid_size: int

    def __init__(
        self: 'HereditaryStratigraphicColumn',
        default_stratum_uid_size: int=64,
    ):
        self._column = []
        self._num_layers_deposited = 0
        self._default_stratum_uid_size = default_stratum_uid_size

        self.DepositLayer()

    def __eq__(self, other,) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def DepositLayer(self: 'HereditaryStratigraphicColumn',) -> None:
        self._column.append(HereditaryStratum(
            deposition_rank=self._num_layers_deposited,
            uid_size=self._default_stratum_uid_size,
        ))
        self._num_layers_deposited += 1

    def GetColumnSize(self: 'HereditaryStratigraphicColumn',) -> int:
        return len(self._column)

    def GetNumLayersDeposited(self: 'HereditaryStratigraphicColumn',) -> int:
        return self._num_layers_deposited

    def CalcLastCommonRankWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:

        self_column_idx = 0
        other_column_idx = 0
        last_common_rank = None

        # helper lambdas
        rank_at = lambda which, idx: which._column[idx].GetDepositionRank()
        uid_at = lambda which, idx: which._column[idx].GetUid()

        while (
            self_column_idx < self.GetColumnSize()
            and other_column_idx < other.GetColumnSize()
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

    def CalcFirstDisparateRankWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:

        self_column_idx = 0
        other_column_idx = 0
        last_common_rank = None

        # helper lambdas
        rank_at = lambda which, idx: which._column[idx].GetDepositionRank()
        uid_at = lambda which, idx: which._column[idx].GetUid()
        column_idxs_bounds_check = lambda: (
            self_column_idx < self.GetColumnSize()
            and other_column_idx < other.GetColumnSize()
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
                    return rank_at(self, self_column_idx)
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

        if self_column_idx < self.GetColumnSize():
            # although no mismatching strata are found between self and other
            # self has strata ranks beyond the newest found in other
            return rank_at(self, self_column_idx)
        elif other_column_idx < other.GetColumnSize():
            # although no mismatching strata are found between other and self
            # other has strata ranks beyond the newest found in self
            return rank_at(other, other_column_idx)
        else:
            # no disparate strata found
            # and self and other have the same newest rank
            return None

    def CalcMrcaRankBoundsWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Tuple[typing.Optional[int], typing.Optional[int],]:

        return (
            self.CalcLastCommonRankWith(other,),
            self.CalcFirstDisparateRankWith(other,),
        )

    def CalcRanksSinceLastCommonalityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:

        last_common_rank = self.CalcLastCommonRankWith(other,)
        if last_common_rank is None: return None
        else:
            assert self.GetNumLayersDeposited()
            res = self.GetNumLayersDeposited() - 1 - last_common_rank
            assert 0 <= res < self.GetNumLayersDeposited()
            return res

    # note, returns -1 if disparity is that other has advanced to ranks
    # past self's largest rank
    def CalcRanksSinceFirstDisparityWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Optional[int]:

        first_disparate_rank = self.CalcFirstDisparateRankWith(other,)
        if first_disparate_rank is None: return None
        else:
            assert self.GetNumLayersDeposited()
            res = self.GetNumLayersDeposited() - 1 - first_disparate_rank
            assert -1 <= res < self.GetNumLayersDeposited()
            return res


    def CalcRanksSinceMrcaBoundsWith(
        self: 'HereditaryStratigraphicColumn',
        other: 'HereditaryStratigraphicColumn',
    ) -> typing.Tuple[typing.Optional[int], typing.Optional[int],]:
        return (
            self.CalcRanksSinceLastCommonalityWith(other,),
            self.CalcRanksSinceFirstDisparityWith(other,),
        )
