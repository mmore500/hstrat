import typing


class StratumRetentionPredicateMinimal:

    def __call__(
        self: 'StratumRetentionPredicateMinimal',
        stratum_rank: int,
        column_layers_deposited: int,
    ) -> bool:
        return stratum_rank in (0, column_layers_deposited)

    def __eq__(
        self: 'StratumRetentionPredicateMinimal',
        other: 'StratumRetentionPredicateMinimal',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def CalcColumnSizeUpperBound(
        self: 'StratumRetentionPredicateMinimal',
        num_layers_deposited: typing.Optional[int]=None,
    ) -> int:
        return 2

    def CalcMrcaUncertaintyUpperBound(
        self: 'StratumRetentionPredicateMinimal',
        *,
        first_num_layers_deposited: int,
        second_num_layers_deposited: int,
        actual_rank_of_mrca: typing.Optional[int]=None,
    ) -> int:
        # essentially, no guarantee given
        return max(
            first_num_layers_deposited,
            second_num_layers_deposited,
        )

    def CalcRankAtColumnIndex(
        self: 'StratumRetentionPredicateMinimal',
        index: int,
        num_layers_deposited: int,
    ) -> int:
        return [
            0,
            num_layers_deposited - 1,
            num_layers_deposited,
        ][index]
