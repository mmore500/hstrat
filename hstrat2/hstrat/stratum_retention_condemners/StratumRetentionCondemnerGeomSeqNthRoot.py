import typing

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicateGeomSeqNthRoot


class StratumRetentionCondemnerGeomSeqNthRoot(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicateGeomSeqNthRoot,
):
    """TODO

    See Also
    --------
    StratumRetentionPredicateGeomSeqNthRoot:
        For definitions of methods inherited by this class that describe
        guaranteed properties of the nth root geometric sequence stratum retention
        policy.
    """

    def __init__(
        self: 'StratumRetentionCondemnerGeomSeqNthRoot',
        degree: int=100,
        interspersal: int=2,
    ):
        """Construct the functor.

        Parameters
        ----------
        degree : int, optional
            TODO.
        interspersal : int, optional
            TODO.
        """

        super(
            StratumRetentionCondemnerGeomSeqNthRoot,
            self,
        ).__init__(
            degree=degree,
            interspersal=interspersal,
        )

    def __call__(
        self: 'StratumRetentionCondemnerGeomSeqNthRoot',
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
        StratumRetentionPredicateGeomSeqNthRoot:
            For details on the rationale, implementation, and guarantees of the
            nth root geometric sequence stratum retention policy.
        """

        prev_retained_ranks = super(
            StratumRetentionCondemnerGeomSeqNthRoot,
            self,
        )._get_retained_ranks(
            num_stratum_depositions_completed,
        )

        cur_retained_ranks = super(
            StratumRetentionCondemnerGeomSeqNthRoot,
            self,
        )._get_retained_ranks(
            num_stratum_depositions_completed + 1,
        )

        # take set difference between prev retained ranks and cur retained ranks
        yield from (prev_retained_ranks - cur_retained_ranks)
