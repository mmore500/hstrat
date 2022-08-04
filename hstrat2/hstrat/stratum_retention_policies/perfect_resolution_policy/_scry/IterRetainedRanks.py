import typing

from ..PolicySpec import PolicySpec

class IterRetainedRanks:

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
        num_strata_deposited: typing.Optional[int],
    ) -> typing.Iterator[int]:
        """Iterate over retained strata ranks at `num_strata_deposited` in
        ascending order."""

        yield from range(num_strata_deposited)
