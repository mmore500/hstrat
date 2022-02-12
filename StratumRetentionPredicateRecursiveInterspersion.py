import math
import typing


class StratumRetentionPredicateRecursiveInterspersion:

    _min_intervals_divide_into: int
    _num_intervals_recurse_on: int

    def __init__(
        self: 'StratumRetentionPredicateRecursiveInterspersion',
        min_intervals_divide_into: int=10,
        num_intervals_recurse_on: int=5,
    ):
      assert min_intervals_divide_into > 0
      assert num_intervals_recurse_on < min_intervals_divide_into

      self._min_intervals_divide_into = min_intervals_divide_into
      self._num_intervals_recurse_on = num_intervals_recurse_on

    def __eq__(
        self: 'StratumRetentionPredicateRecursiveInterspersion',
        other: 'StratumRetentionPredicateRecursiveInterspersion',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __call__(
        self: 'StratumRetentionPredicateRecursiveInterspersion',
        stratum_rank: int,
        column_strata_deposited: int,
    ) -> bool:

        if stratum_rank==column_strata_deposited: return True

        if column_strata_deposited <= self._min_intervals_divide_into:
            return True

        cur_stage = math.ceil(math.log(
            (column_strata_deposited)/self._min_intervals_divide_into,
            2,
        ))
        cur_stage_smallest = 2**(cur_stage-1) * self._min_intervals_divide_into

        assert cur_stage_smallest % self._min_intervals_divide_into == 0
        cur_stage_interval_size = (
            cur_stage_smallest // self._min_intervals_divide_into
        )

        num_complete_intervals = (
            column_strata_deposited // cur_stage_interval_size
        )

        num_intervals = (column_strata_deposited+1) // cur_stage_interval_size

        stratum_interval = stratum_rank // cur_stage_interval_size

        if stratum_rank % cur_stage_interval_size == 0: return True
        # TODO there's an off by one in here with self._num_intervals_recurse_on
        elif (
            stratum_interval + 1
            >= num_complete_intervals - self._num_intervals_recurse_on
        ):
            strip = (
                (num_complete_intervals - 1 - self._num_intervals_recurse_on)
                * cur_stage_interval_size
            )
            return self(
              stratum_rank - strip,
              column_strata_deposited - strip,
            )
        else:
            return False

    def CalcNumStrataRetainedUpperBound(
        self: 'StratumRetentionPredicateRecursiveInterspersion',
        num_strata_deposited: int,
    ) -> int:

        if num_strata_deposited <= self._min_intervals_divide_into:
            return self._min_intervals_divide_into

        base = self._min_intervals_divide_into / self._num_intervals_recurse_on
        num_recursive_stages = int(math.floor(math.log(
            num_strata_deposited / self._min_intervals_divide_into,
            base,
        )))
        return num_recursive_stages * (2 * self._min_intervals_divide_into) + 2

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateRecursiveInterspersion',
        *,
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> int:
        # essentially, no guarantee given
        return max(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )
