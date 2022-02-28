import typing

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicateFixedResolution


class StratumRetentionCondemnerFixedResolution(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicateFixedResolution,
):
    """Functor to implement the fixed resolution stratum retention policy, for
    use with HereditaryStratigraphicColumn.

    This functor enacts the fixed resolution policy by specifying the set of
    strata ranks that should be purged from a hereditary stratigraphic column
    when the nth stratum is deposited.

    The fixed resolution policy ensures estimates of MRCA rank will have
    uncertainty bounds less than or equal a fixed, absolute user-specified cap
    that is independent of the number of strata deposited on either column.
    Thus, MRCA rank estimate uncertainty scales as O(1) with respect to the
    greater number of strata deposited on either column.

    Under the fixed resolution policy, the number of strata retained (i.e.,
    space complexity) scales as O(n) with respect to the number of strata
    deposited.

    See Also
    --------
    StratumRetentionPredicateFixedResolution:
        For definitions of methods inherited by this class that describe
        guaranteed properties of the fixed resolution stratum retention
        policy.
    """

    def __init__(
        self: 'StratumRetentionCondemnerFixedResolution',
        fixed_resolution: int=10,
    ):
        """Construct the functor.

        Parameters
        ----------
        fixed_resolution : int, optional
            The rank interval strata should be retained at. The uncertainty of
            MRCA estimates provided under the fixed resolution policy will
            always be strictly less than this cap.
        """

        super(
            StratumRetentionCondemnerFixedResolution,
            self,
        ).__init__(
            fixed_resolution=fixed_resolution,
        )

    def __call__(
        self: 'StratumRetentionCondemnerFixedResolution',
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
        StratumRetentionPredicateFixedResolution:
            For details on the rationale, implementation, and guarantees of the
            fixed resolution stratum retention policy.
        """

        resolution = self._fixed_resolution
        # _fixed_resolution is from super class

        # in-progress deposition not reflected in
        # num_stratum_depositions_completed
        second_newest_stratum_rank = num_stratum_depositions_completed - 1
        if (
            second_newest_stratum_rank > 0
            and second_newest_stratum_rank % resolution
        ):
            yield second_newest_stratum_rank
