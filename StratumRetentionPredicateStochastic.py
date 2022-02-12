import random


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
