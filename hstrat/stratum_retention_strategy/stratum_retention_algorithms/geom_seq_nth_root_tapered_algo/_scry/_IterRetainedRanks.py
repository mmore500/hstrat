import typing

from ....._auxiliary_lib import memoize_generator
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

    def __hash__(self: "IterRetainedRanks") -> int:
        """Hash object instance."""
        return 0

    def __eq__(self: "IterRetainedRanks", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    @memoize_generator()
    def __call__(
        self: "IterRetainedRanks",
        policy: PolicyCouplerBase,
        num_strata_deposited: int,
    ) -> typing.Iterator[int]:
        """Iterate over retained strata ranks at `num_strata_deposited` in
        ascending order."""
        yield from sorted(
            get_retained_ranks(
                policy,
                num_strata_deposited,
            )
        )
