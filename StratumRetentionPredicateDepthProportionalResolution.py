import math

class StratumRetentionPredicateDepthProportionalResolution():

    _min_intervals_divide_into: int
    _num_intervals_recurse_on: int

    def __init__(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        min_intervals_divide_into: int=10
    ):
      assert min_intervals_divide_into > 0

      self._min_intervals_divide_into = min_intervals_divide_into


    def __eq__(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        other: 'StratumRetentionPredicateDepthProportionalResolution',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


    def __call__(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        stratum_rank: int,
        column_layers_deposited: int,
    ) -> bool:

        if stratum_rank==column_layers_deposited-1: return True

        if column_layers_deposited < self._min_intervals_divide_into:
            return True

        cur_stage = math.ceil(math.log(
            (column_layers_deposited+1)/self._min_intervals_divide_into,
            2,
        ))
        cur_stage_smallest = 2**(cur_stage-1) * self._min_intervals_divide_into

        assert cur_stage_smallest % self._min_intervals_divide_into == 0
        cur_stage_interval_size = (
            cur_stage_smallest // self._min_intervals_divide_into
        )

        num_complete_intervals = (
            column_layers_deposited // cur_stage_interval_size
        )

        num_intervals = (column_layers_deposited+1) // cur_stage_interval_size

        stratum_interval = stratum_rank // cur_stage_interval_size

        return stratum_rank % cur_stage_interval_size == 0
