import typing

from ..PolicySpec import PolicySpec

class CalcNumStrataRetainedUpperBound:

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
        policy: typing.Optional['Policy'],
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposted?"""

        return num_strata_deposited
