import typing

from .._impl import get_retained_ranks
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
        return isinstance(other, self.__class__)

    def __call__(
        self: 'IterRetainedRanks',
        policy: 'Policy',
        num_strata_deposited: int,
    ) -> typing.Iterator[int]:
        """Iterate over retained strata ranks at `num_strata_deposited` in
        ascending order."""

        spec = policy.GetSpec()

        yield from sorted(get_retained_ranks(
            spec._degree,
            spec._interspersal,
            num_strata_deposited,
        ))
