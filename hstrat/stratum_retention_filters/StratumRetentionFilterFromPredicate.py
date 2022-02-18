import typing

from ..HereditaryStratum import HereditaryStratum


class _StratumRetentionFilterFromPredicateBase:
    pass


def StratumRetentionFilterFromPredicate(predicate: typing.Callable):

    class StratumRetentionFilterFromPredicate(
        _StratumRetentionFilterFromPredicateBase,
    ):
        _predicate: typing.Callable

        def __init__(
            self: 'StratumRetentionFilterFromPredicate',
            predicate: typing.Callable,
        ):
            self._predicate = predicate

        def __call__(
            self: 'StratumRetentionFilterFromPredicate',
            strat_col: 'HereditaryStratigraphicColumn',
        ) -> typing.List[HereditaryStratum]:
            # wrapper to enforce requirements on predicate
            def should_retain(stratum_rank: int) -> bool:
                res = self._predicate(
                    stratum_rank=stratum_rank,
                    column_strata_deposited=strat_col.GetNumStrataDeposited(),
                )
                # predicate must *always* retain the initial and latest strata
                if stratum_rank in (0, strat_col.GetNumStrataDeposited()):
                    assert res
                return res

            return [
                entry
                for idx, entry in enumerate(strat_col._column)
                if should_retain(strat_col.CalcRankAtColumnIndex(idx))
            ]


        def __eq__(
            self: 'StratumRetentionFilterFromPredicate',
            other: 'StratumRetentionFilterFromPredicate',
        ) -> bool:
            if issubclass(
                other.__class__,
                _StratumRetentionFilterFromPredicateBase,
            ):
                return self._predicate == other._predicate
            else:
                return False

        if hasattr(predicate, 'CalcNumStrataRetainedUpperBound'):
            def CalcNumStrataRetainedUpperBound(
                self: 'StratumRetentionFilterFromPredicate',
                num_strata_deposited: int,
            ) -> int:
                return self._predicate.CalcNumStrataRetainedUpperBound(
                    num_strata_deposited=num_strata_deposited,
                )

        if hasattr(predicate, 'CalcMrcaUncertaintyUpperBound'):
            def CalcMrcaUncertaintyUpperBound(
                self: 'StratumRetentionFilterFromPredicate',
                *,
                first_num_strata_deposited: int,
                second_num_strata_deposited: int,
                actual_rank_of_mrca: int,
            ) -> int:
                return self._predicate.CalcMrcaUncertaintyUpperBound(
                    first_num_strata_deposited=first_num_strata_deposited,
                    second_num_strata_deposited=second_num_strata_deposited,
                    actual_rank_of_mrca=actual_rank_of_mrca,
                )

        if hasattr(predicate, 'CalcRankAtColumnIndex'):
            def CalcRankAtColumnIndex(
                self: 'StratumRetentionPredicateMaximal',
                index: int,
                num_strata_deposited: int,
            ) -> int:
                return self._predicate.CalcRankAtColumnIndex(
                    index=index,
                    num_strata_deposited=num_strata_deposited,
                )

    return StratumRetentionFilterFromPredicate(predicate)
