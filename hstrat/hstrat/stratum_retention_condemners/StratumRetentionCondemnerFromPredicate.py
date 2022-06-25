import typing

from ..HereditaryStratum import HereditaryStratum


class _StratumRetentionCondemnerFromPredicateBase:
    """Dummy class to faciliate recognition of instantiations of the
    StratumRetentionCondemnerFromPredicate class across different calls to
    the StratumRetentionCondemnerFromPredicate factory."""

    pass


def StratumRetentionCondemnerFromPredicate(predicate: typing.Callable):
    """Factory method to generate a stratum retention condemner functor from a
    stratum retention predicate functor.

    Parameters
    ----------
    predicate : callable
        Callable specifying whether a stratum with deposition rank r should be
        retained within the hereditary stratigraphic column after n strata have
        been deposited.

    Returns
    -------
    condemner : callable
        Functor that enacts the predicate's stratum retention policy by
        specifying the set of strata ranks that should be purged from a
        hereditary stratigraphic column when the nth stratum is deposited.
    """

    class StratumRetentionCondemnerFromPredicate(
        _StratumRetentionCondemnerFromPredicateBase,
    ):
        """Functor that wraps a stratum retention predicate functor to
        operate as a stratum retention condemner."""

        _predicate: typing.Callable

        def __init__(
            self: 'StratumRetentionCondemnerFromPredicate',
            predicate: typing.Callable,
        ):
            """Construct the functor.

            Parameters
            ----------
            predicate : callable
                Callable specifying whether a stratum with deposition rank r
                should be retained within the hereditary stratigraphic column
                after n strata have been deposited.
            """

            self._predicate = predicate

        def __call__(
            self: 'StratumRetentionCondemnerFromPredicate',
            num_stratum_depositions_completed: int,
            retained_ranks: typing.Iterable[int],
        ) -> typing.Iterator[int]:


            def should_retain(stratum_rank: int) -> bool:
                """Should the rth stratum rank be retained?

                Asserts retention requirements are respected by predicate.
                """
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
            """Compare for value-wise equality."""

            # account for possible distinct instantiations of the
            # StratumRetentionCondemnerFromPredicate class across calls to the
            # StratumRetentionCondemnerFromPredicate factory
            if issubclass(
                other.__class__,
                _StratumRetentionCondemnerFromPredicateBase,
            ):
                return self._predicate == other._predicate
            else:
                return False

        if hasattr(predicate, 'CalcNumStrataRetainedExact'):
            def CalcNumStrataRetainedExact(
                self: 'StratumRetentionCondemnerFromPredicate',
                num_strata_deposited: int,
            ) -> int:
                """Forwarding wrapper for predicate's
                CalcNumStrataRetainedExact method, if available."""

                return self._predicate.CalcNumStrataRetainedExact(
                    num_strata_deposited=num_strata_deposited,
                )

        if hasattr(predicate, 'CalcNumStrataRetainedUpperBound'):
            def CalcNumStrataRetainedUpperBound(
                self: 'StratumRetentionCondemnerFromPredicate',
                num_strata_deposited: int,
            ) -> int:
                """Forwarding wrapper for predicate's
                CalcNumStrataRetainedUpperBound method, if available."""

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
                """Forwarding wrapper for predicate's
                CalcMrcaUncertaintyUpperBound method, if available."""

                return self._predicate.CalcMrcaUncertaintyUpperBound(
                    first_num_strata_deposited=first_num_strata_deposited,
                    second_num_strata_deposited=second_num_strata_deposited,
                    actual_rank_of_mrca=actual_rank_of_mrca,
                )

        if hasattr(predicate, 'CalcRankAtColumnIndex'):
            def CalcRankAtColumnIndex(
                self: 'StratumRetentionCondemnerFromPredicate',
                index: int,
                num_strata_deposited: int,
            ) -> int:
                """Forwarding wrapper for predicate's CalcRankAtColumnIndex
                method, if available."""

                return self._predicate.CalcRankAtColumnIndex(
                    index=index,
                    num_strata_deposited=num_strata_deposited,
                )

    return StratumRetentionCondemnerFromPredicate(predicate)
