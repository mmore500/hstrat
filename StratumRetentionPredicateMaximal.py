class StratumRetentionPredicateMaximal:

    def __call__(
        self: 'StratumRetentionPredicateMaximal',
        stratum_rank: int,
        column_layers_deposited: int,
    ) -> bool:
        return True

    def __eq__(
        self: 'StratumRetentionPredicateMaximal',
        other: 'StratumRetentionPredicateMaximal',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
