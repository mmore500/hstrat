import typing

from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec


class CalcNumStrataRetainedExact:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "CalcNumStrataRetainedExact",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(self: "CalcNumStrataRetainedExact", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcNumStrataRetainedExact",
        policy: PolicyCouplerBase,
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposited?"""
        spec = policy.GetSpec()

        if num_strata_deposited == 0:
            return 0

        uncertainty = spec.GetFixedResolution()
        newest_stratum_rank = num_strata_deposited - 1
        # +1 for 0'th rank stratum
        num_strata_at_uncertainty_intervals = (
            newest_stratum_rank // uncertainty + 1
        )
        newest_stratum_distinct_from_uncertainty_intervals = (
            newest_stratum_rank % uncertainty != 0
        )
        return (
            num_strata_at_uncertainty_intervals
            + newest_stratum_distinct_from_uncertainty_intervals
        )
