import math
import typing


class StratumRetentionPredicateDepthProportionalResolution():

    _guaranteed_depth_proportional_resolution: int

    def __init__(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        guaranteed_depth_proportional_resolution: int=10
    ):
        assert guaranteed_depth_proportional_resolution > 0
        self._guaranteed_depth_proportional_resolution = (
            guaranteed_depth_proportional_resolution
        )


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

        min_intervals_divide_into = (
            self._guaranteed_depth_proportional_resolution
        )

        if stratum_rank==column_layers_deposited-1: return True

        if column_layers_deposited < min_intervals_divide_into:
            return True

        cur_stage = math.ceil(math.log(
            (column_layers_deposited+1)/min_intervals_divide_into,
            2,
        ))
        cur_stage_smallest = 2**(cur_stage-1) * min_intervals_divide_into

        assert cur_stage_smallest % min_intervals_divide_into == 0
        cur_stage_interval_size = (
            cur_stage_smallest // min_intervals_divide_into
        )

        num_complete_intervals = (
            column_layers_deposited // cur_stage_interval_size
        )

        num_intervals = (column_layers_deposited+1) // cur_stage_interval_size

        stratum_interval = stratum_rank // cur_stage_interval_size

        return stratum_rank % cur_stage_interval_size == 0

    def CalcColumnSizeUpperBound(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        num_layers_deposited: typing.Optional[int]=None,
    ) -> float:
        return self._guaranteed_depth_proportional_resolution * 2 + 2

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateDepthProportionalResolution',
        *,
        first_num_layers_deposited: int,
        second_num_layers_deposited: int,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> float:
        return max(
            first_num_layers_deposited,
            second_num_layers_deposited,
        ) / self._guaranteed_depth_proportional_resolution
