import typing

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicateFixedResolution


class StratumRetentionCondemnerFixedResolution(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicateFixedResolution,
):

    def __init__(
        self: 'StratumRetentionCondemnerFixedResolution',
        fixed_resolution: int=10,
    ):
        super(
            StratumRetentionCondemnerFixedResolution,
            self,
        ).__init__(
            fixed_resolution=fixed_resolution,
        )

    def __call__(
        self: 'StratumRetentionCondemnerFixedResolution',
        num_strata_deposited: int,
        retained_ranks: typing.Optional[typing.Iterable[int]]=None,
    ) -> typing.Iterator[int]:
        resolution = self._fixed_resolution
        # _fixed_resolution is from super class

        # in-progress deposition not reflected in num_strata_deposited
        second_newest_stratum_rank = num_strata_deposited - 1
        if (
            second_newest_stratum_rank > 0
            and second_newest_stratum_rank % resolution
        ):
            yield second_newest_stratum_rank
