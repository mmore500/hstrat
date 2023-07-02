import typing

from ...._detail import PolicyCouplerBase
from ..._PolicySpec import PolicySpec
from ..._impl import calc_provided_uncertainty


class IterRetainedRanksReference:
    """Functor to provide member function implementation in Policy class.

    Provides a more concise, simpler to reason about implementation.
    """

    def __init__(
        self: "IterRetainedRanksReference",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(self: "IterRetainedRanksReference", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "IterRetainedRanksReference",
        policy: PolicyCouplerBase,
        num_strata_deposited: int,
    ) -> typing.Iterator[int]:
        """Iterate over retained strata ranks at `num_strata_deposited` in
        ascending order."""
        spec = policy.GetSpec()
        resolution = spec.GetRecencyProportionalResolution()

        cur_rank = 0
        last_rank = num_strata_deposited - 1
        while cur_rank <= last_rank:
            yield cur_rank
            # note that calc_provided_uncertainty will never return zero
            cur_rank += calc_provided_uncertainty(
                resolution,
                last_rank - cur_rank,
            )
