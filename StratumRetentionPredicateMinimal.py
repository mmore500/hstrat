

class StratumRetentionPredicateMinimal:

    def __call__(
        self: 'StratumRetentionPredicateMinimal',
        stratum_rank: int,
        column_layers_deposited: int,
    ) -> bool:
        return stratum_rank in (0, column_layers_deposited - 1,)

    def __eq__(
        self: 'StratumRetentionPredicateMinimal',
        other: 'StratumRetentionPredicateMinimal',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
