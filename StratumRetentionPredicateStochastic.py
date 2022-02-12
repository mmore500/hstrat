import random
import typing


class StratumRetentionPredicateStochastic:

    def __call__(
        self: 'StratumRetentionPredicateStochastic',
        stratum_rank: int,
        column_layers_deposited: int,
    ) -> bool:
        if stratum_rank and stratum_rank == column_layers_deposited - 2:
            return random.choice([True, False])
        else: return True

    def __eq__(
        self: 'StratumRetentionPredicateStochastic',
        other: 'StratumRetentionPredicateStochastic',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcColumnSizeUpperBound(
        self: 'StratumRetentionPredicateStochastic',
        num_layers_deposited: int,
    ) -> float:
        return num_layers_deposited

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateStochastic',
        *,
        first_num_layers_deposited: int,
        second_num_layers_deposited: int,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> float:
        # essentially, no guarantee given
        return max(
            first_num_layers_deposited,
            second_num_layers_deposited,
        )
