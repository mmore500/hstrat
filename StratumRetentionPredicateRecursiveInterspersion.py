import math
import typing

from .StratumRetentionPredicateDepthProportionalResolution \
    import StratumRetentionPredicateDepthProportionalResolution

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

        if stratum_rank == column_strata_deposited: return True

        if column_strata_deposited <= self._min_intervals_divide_into:
            return True

        depth_predicate = StratumRetentionPredicateDepthProportionalResolution(
            guaranteed_depth_proportional_resolution
                = self._min_intervals_divide_into,
        )
        interval_size = depth_predicate._calc_provided_uncertainty(
            column_strata_deposited,
        )
        stratum_interval = stratum_rank // interval_size
        num_complete_intervals = column_strata_deposited // interval_size
        num_complete_intervals_after_stratum = (
            num_complete_intervals - stratum_interval
        )

        if depth_predicate(stratum_rank, column_strata_deposited):
            return True
        elif (
            num_complete_intervals_after_stratum
            <= self._num_intervals_recurse_on
        ):
            num_intervals_excluded = (
                num_complete_intervals
                - self._num_intervals_recurse_on
            )
            num_strata_excluded = (
                num_intervals_excluded * interval_size
            )
            return self(
              stratum_rank - num_strata_excluded,
              column_strata_deposited - num_strata_excluded,
            )
        else: return False

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
