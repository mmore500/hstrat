import math
import typing

from .StratumRetentionPredicateRecursiveInterspersion \
    import StratumRetentionPredicateRecursiveInterspersion

class StratumRetentionPredicateRecencyProportionalResolution(
    StratumRetentionPredicateRecursiveInterspersion,
):

    _guaranteed_mrca_recency_proportional_resolution: int

    def __init__(
        self: 'StratumRetentionPredicateRecencyProportionalResolution',
        guaranteed_mrca_recency_proportional_resolution: int=10,
    ):
        self._guaranteed_mrca_recency_proportional_resolution = (
            guaranteed_mrca_recency_proportional_resolution
        )
        min_intervals_divide_into = (
            guaranteed_mrca_recency_proportional_resolution * 2
        )
        num_intervals_recurse_on = min_intervals_divide_into // 2

        super(
            StratumRetentionPredicateRecencyProportionalResolution,
            self,
        ).__init__(
            min_intervals_divide_into=min_intervals_divide_into,
            num_intervals_recurse_on=num_intervals_recurse_on,
        )

    def __eq__(
        self: 'StratumRetentionPredicateRecencyProportionalResolution',
        other: 'StratumRetentionPredicateRecencyProportionalResolution',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateRecencyProportionalResolution',
        *,
        actual_rank_of_mrca: int,
        first_num_layers_deposited: int,
        second_num_layers_deposited: int,
    ) -> float:
        max_ranks_since_mrca = max(
            first_num_layers_deposited,
            second_num_layers_deposited,
        ) - actual_rank_of_mrca
        return (
            max_ranks_since_mrca
            / self._guaranteed_mrca_recency_proportional_resolution
        )
