import math
import typing

from ..PolicySpec import PolicySpec

class CalcNumStrataRetainedUpperBound:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: 'CalcNumStrataRetainedUpperBound',
        policy_spec: typing.Optional[PolicySpec]=None,
    ) -> None:
        pass

    def __eq__(
        self: 'CalcNumStrataRetainedUpperBound',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, CalcNumStrataRetainedUpperBound)

    def __call__(
        self: 'CalcNumStrataRetainedUpperBound',
        policy: 'Policy',
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposted?. Inclusive."""

        spec = policy.GetSpec()
        resolution = spec._guaranteed_mrca_recency_proportional_resolution

        return int(
            (resolution + 1) * math.log2(num_strata_deposited - 1)
            - sum(math.log2(r + 1) for r in range(resolution))
            + 1
        ) if num_strata_deposited > resolution + 1 else num_strata_deposited
