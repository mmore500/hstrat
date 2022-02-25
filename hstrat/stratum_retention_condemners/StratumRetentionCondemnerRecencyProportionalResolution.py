import typing

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicateRecencyProportionalResolution


class StratumRetentionCondemnerRecencyProportionalResolution(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicateRecencyProportionalResolution,
):
    """Functor to implement the MRCA-recency-proportional resolution stratum retention policy, for use with HereditaryStratigraphicColumn.

    This functor enacts the MRCA-recency-proportional resolution policy by
    specifying the set of strata ranks that should be purged from a hereditary
    stratigraphic column when the nth stratum is deposited.

    The MRCA-recency-proportional resolution policy ensures estimates of MRCA
    rank will have uncertainty bounds less than or equal to a user-specified
    proportion of the actual number of generations elapsed since the MRCA and
    the deepest of the compared columns. MRCA rank estimate uncertainty scales
    in the worst case scales as O(n) with respect to the greater number of
    strata deposited on either column. However, with respect to estimating the rank of the MRCA when lineages diverged any fixed number of generations ago,
    uncertainty scales as O(1).

    Under the MRCA-recency-proportional resolution policy, the number of strata
    retained (i.e., space complexity) scales as O(log(n)) with respect to the
    number of strata deposited.

    See Also
    --------
    StratumRetentionPredicateRecencyProportionalResolution:
        For definitions of methods inherited by this class that describe
        guaranteed properties of the MRCA-recency proportional resolution
        stratum retention policy.
    """

    def __init__(
        self: 'StratumRetentionCondemnerRecencyProportionalResolution',
        guaranteed_mrca_recency_proportional_resolution: int=10,
    ):
        """Construct the functor.

        Parameters
        ----------
        guaranteed_mrca_recency_proportional_resolution : int, optional
            The desired minimum number of intervals between the MRCA and the
            deeper compared column to be able to be distinguished between. The
            uncertainty of MRCA rank estimates provided under the MRCA-recency-
            proportional resolution policy will scale as the actual
            phylogenetic depth of the MRCA divided by
            guaranteed_mrca_recency_proportional_resolution.
        """

        super(
            StratumRetentionCondemnerRecencyProportionalResolution,
            self,
        ).__init__(
            guaranteed_mrca_recency_proportional_resolution
                =guaranteed_mrca_recency_proportional_resolution,
        )

    def _num_to_condemn(
        self: 'StratumRetentionCondemnerRecencyProportionalResolution',
        num_stratum_depositions_completed: int,
    ) -> int:
        """How many strata should be eliminated after
        num_stratum_depositions_completed have been deposited and the
        num_stratum_depositions_completed + 1'th deposition is in progress?

        Used to implement functor's __call__ method specifying which ranks
        should be purged during this stratum deposition. This expression for
        exact number deposited was extrapolated from
            * resolution = 0, <https://oeis.org/A001511>
            * resolution = 1, <https://oeis.org/A091090>
        and is unit tested extensively.
        """

        resolution = self._guaranteed_mrca_recency_proportional_resolution
        # _guaranteed_mrca_recency_proportional_resolution is from super class

        if num_stratum_depositions_completed % 2 == 1:
            return 0
        elif num_stratum_depositions_completed < 2 * (resolution + 1):
            return 0
        else:
            return \
                1 + self._num_to_condemn(num_stratum_depositions_completed // 2)

    def __call__(
        self: 'StratumRetentionCondemnerRecencyProportionalResolution',
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
        StratumRetentionPredicateRecencyProportionalResolution:
            For details on the rationale, implementation, and guarantees of the
            recency-proportional resolution stratum retention policy.
        """

        num_to_condemn = self._num_to_condemn(num_stratum_depositions_completed)
        resolution = self._guaranteed_mrca_recency_proportional_resolution
        # _guaranteed_mrca_recency_proportional_resolution is from super class

        for i in range(num_to_condemn):
            factor = 2 * resolution + 1
            num_ranks_back = factor * (2 ** i)
            yield num_stratum_depositions_completed - num_ranks_back
