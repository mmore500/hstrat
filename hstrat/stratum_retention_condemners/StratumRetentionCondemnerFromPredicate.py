import typing

from ..HereditaryStratum import HereditaryStratum


class _StratumRetentionCondemnerFromPredicateBase:
    pass


def StratumRetentionCondemnerFromPredicate(predicate: typing.Callable):

    class StratumRetentionCondemnerFromPredicate(
        _StratumRetentionCondemnerFromPredicateBase,
    ):
        _predicate: typing.Callable

        def __init__(
            self: 'StratumRetentionCondemnerFromPredicate',
            predicate: typing.Callable,
        ):
            self._predicate = predicate

        def __call__(
            self: 'StratumRetentionCondemnerFromPredicate',
            retained_ranks: typing.Iterable[int],
            num_stratum_depositions_completed: int,
        ) -> typing.Iterator[int]:
            # wrapper to enforce requirements on predicate
            def should_retain(stratum_rank: int) -> bool:
                res = self._predicate(
                    stratum_rank=stratum_rank,
                    num_stratum_depositions_completed
                        =num_stratum_depositions_completed,
                )
                # predicate must *always* retain the initial and latest strata
                if stratum_rank in (0, num_stratum_depositions_completed):
                    assert res
                return res

            for rank in retained_ranks:
                if not should_retain(rank):
                    yield rank
            return

        def __eq__(
            self: 'StratumRetentionCondemnerFromPredicate',
            other: 'StratumRetentionCondemnerFromPredicate',
        ) -> bool:
            if issubclass(
                other.__class__,
                _StratumRetentionCondemnerFromPredicateBase,
            ):
                return self._predicate == other._predicate
            else:
                return False

        if hasattr(predicate, 'CalcNumStrataRetainedUpperBound'):
            def CalcNumStrataRetainedUpperBound(
                self: 'StratumRetentionCondemnerFromPredicate',
                num_strata_deposited: int,
            ) -> int:
                return self._predicate.CalcNumStrataRetainedUpperBound(
                    num_strata_deposited=num_strata_deposited,
                )

        if hasattr(predicate, 'CalcMrcaUncertaintyUpperBound'):
            def CalcMrcaUncertaintyUpperBound(
                self: 'StratumRetentionCondemnerFromPredicate',
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
                self: 'StratumCondemnerateMaximal',
                index: int,
                num_strata_deposited: int,
            ) -> int:
                return self._predicate.CalcRankAtColumnIndex(
                    index=index,
                    num_strata_deposited=num_strata_deposited,
                )

    return StratumRetentionCondemnerFromPredicate(predicate)
