import typing

from ...._detail import PolicyCouplerBase
from ..._PolicySpec import PolicySpec
from ..._impl import calc_provided_uncertainty


class IterRetainedRanksProduction:
    """Functor to provide member function implementation in Policy class.

    Optimizes to reduce calls to `calc_provided_uncertainty`.
    """

    def __init__(
        self: "IterRetainedRanksProduction",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(self: "IterRetainedRanksProduction", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "IterRetainedRanksProduction",
        policy: PolicyCouplerBase,
        num_strata_deposited: int,
    ) -> typing.Iterator[int]:
        """Iterate over retained strata ranks at `num_strata_deposited` in
        ascending order."""
        spec = policy.GetSpec()
        resolution = spec.GetRecencyProportionalResolution()

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
