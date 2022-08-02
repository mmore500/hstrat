import typing

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicatePerfectResolution


class StratumRetentionCondemnerPerfectResolution(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicatePerfectResolution,
):
    """Functor to implement the perfect resolution stratum retention policy, for
    use with HereditaryStratigraphicColumn.

    This functor enacts the perfect resolution policy by specifying the set of
    strata ranks that should be purged from a hereditary stratigraphic column
    when the nth stratum is deposited.

    The perfect resolution policy retains all strata. So, comparisons between
    two columns under this policy will detect MRCA rank with zero
    uncertainty. So, MRCA rank estimate uncertainty scales as O(1) with respect
    to the greater number of strata deposited on either column.

    Under the perfect resolution policy, the number of strata retained (i.e.,
    space complexity) scales as O(n) with respect to the number of strata
    deposited.

    See Also
    --------
    StratumRetentionPredicatePerfectResolution:
        For definitions of methods inherited by this class that describe
        guaranteed properties of the perfect resolution stratum retention
        policy.
    """

    def __call__(
        self: 'StratumRetentionCondemnerPerfectResolution',
        num_stratum_depositions_completed: typing.Optional[int]=None,
        retained_ranks: typing.Optional[typing.Iterable[int]]=None,
    ) -> typing.Iterator[int]:
        """Decide which strata within the stratagraphic column should be purged.

        Every time a new stratum is deposited, this method is called to
        determine which strata should be purged. All strata at ranks yielded
        from this functor are immediately purged from the column, meaning that
        for a stratum to persist it must not be yielded by this functor each
        and every time a new stratum is deposited.

        Parameters
        ----------
        num_stratum_depositions_completed : int
            The number of strata that have already been deposited, not
            including the latest stratum being deposited which prompted the
            current purge operation.
        retained_ranks : iterator over int, optional
            An iterator over ranks of strata currently retained within the
            hereditary stratigraphic column. Not used in this functor.

        Returns
        -------
        iterator over int
                The ranks of strata that should be purged from the hereditary
            stratigraphic column at this deposition step.

        See Also
        --------
        StratumRetentionPredicatePerfectResolution:
            For details on the rationale, implementation, and guarantees of the
            perfect resolution stratum retention policy.
        """

        # empty generator
        # see https://stackoverflow.com/a/13243870/17332200
        return
        yield
