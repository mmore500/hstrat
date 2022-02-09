import math
import typing

from . import HereditaryStratum

class HereditaryStratigraphicColumn:

    _column: typing.List[HereditaryStratum,]
    _num_layers_deposited: int
    _default_stratum_uid_size: int

    def __init__(
        self,
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

    def DepositLayer(self,) -> None:
        self._column.append(HereditaryStratum(
            deposition_rank=self._num_layers_deposited,
            uid_size=self._default_stratum_uid_size,
        ))
        self._num_layers_deposited += 1

    def GetColumnSize(self,) -> int:
        return len(self._column)

    def GetNumLayersDeposited(self,) -> int:
        return self._num_layers_deposited

    def GetLastCommonRankWith(self, other,) -> typing.Optional[int]:

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

    def GetFirstDisparateRankWith(self, other,) -> typing.Optional[int]:

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

        # no disparate rank found
        return None

    def GetMrcaRankBoundsWith(
        self,
        other,
    ) -> typing.Tuple[typing.Optional[int], typing.Optional[int],]:

        return (
            self.GetLastCommonRankWith(other,),
            self.GetFirstDisparateRankWith(other,),
        )
