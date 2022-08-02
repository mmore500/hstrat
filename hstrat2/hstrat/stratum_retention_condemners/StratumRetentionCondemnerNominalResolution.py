import typing

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicateNominalResolution


class StratumRetentionCondemnerNominalResolution(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicateNominalResolution,
):
    """Functor to implement the nominal resolution stratum retention policy, for
    use with HereditaryStratigraphicColumn.

    This functor enacts the nominal resolution policy by specifying the set of
    strata ranks that should be purged from a hereditary stratigraphic column
    when the nth stratum is deposited.

    The nominal resolution policy only retains the most ancient (i.e., very
    first) and most recent (i.e., last) strata. So, comparisons between two
    columns under this policy will only be able to detect whether they share
    any common ancestor and whether they are from the same organism (i.e., no
    generations have elapsed since the MRCA). Thus, MRCA rank estimate
    uncertainty scales as O(n) with respect to the greater number of strata deposited on either column.

    Under the nominal resolution policy, the number of strata retained (i.e.,
    space complexity) scales as O(1) with respect to the number of strata
    deposited.

    See Also
    --------
    StratumRetentionPredicateNominalResolution:
        For definitions of methods inherited by this class that describe
        guaranteed properties of the nominal resolution stratum retention
        policy.
    """

    def __call__(
        self: 'StratumRetentionCondemnerNominalResolution',
        num_stratum_depositions_completed: int,
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
        StratumRetentionPredicateNominalResolution:
            For details on the rationale, implementation, and guarantees of the
            nominal resolution stratum retention policy.
        """

        # in-progress deposition not reflected in
        # num_stratum_depositions_completed
        if num_stratum_depositions_completed > 1:
            yield num_stratum_depositions_completed - 1
