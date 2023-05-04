import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec
from .._impl import calc_provided_uncertainty


class IterRetainedRanks:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "IterRetainedRanks",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(self: "IterRetainedRanks", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "IterRetainedRanks",
        policy: PolicyCouplerBase,
        num_strata_deposited: int,
    ) -> typing.Iterator[int]:
        """Iterate over retained strata ranks at `num_strata_deposited` in
        ascending order."""
        spec = policy.GetSpec()
        uncertainty = calc_provided_uncertainty(
            spec.GetDepthProportionalResolution(),
            num_strata_deposited,
        )

        yield from range(0, num_strata_deposited, uncertainty)

        last_rank = num_strata_deposited - 1
        if last_rank > 0 and last_rank % uncertainty:
            yield last_rank
