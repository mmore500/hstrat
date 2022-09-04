import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec
from .._impl import get_retained_ranks


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

        yield from sorted(
            get_retained_ranks(
                spec.GetDegree(),
                spec.GetInterspersal(),
                num_strata_deposited,
            )
        )
