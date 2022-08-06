import typing

from .._impl import calc_provided_uncertainty
from ..PolicySpec import PolicySpec

class IterRetainedRanks:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: 'IterRetainedRanks',
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(
        self: 'IterRetainedRanks',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, IterRetainedRanks)

    def __call__(
        self: 'IterRetainedRanks',
        policy: typing.Optional['Policy'],
        num_strata_deposited: int,
    ) -> typing.Iterator[int]:
        """Iterate over retained strata ranks at `num_strata_deposited` in
        ascending order."""

        spec = policy.GetSpec()
        resolution = spec._guaranteed_mrca_recency_proportional_resolution

        cur_rank = 0
        last_rank = num_strata_deposited - 1
        while last_rank - cur_rank > resolution:
            yield cur_rank
            cur_rank += calc_provided_uncertainty(
                resolution,
                last_rank - cur_rank,
            )

        yield from range(
            max(last_rank - resolution, 0),
            num_strata_deposited,
        )
