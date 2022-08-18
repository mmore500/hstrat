import itertools as it
import typing

from ..PolicySpec import PolicySpec


class CalcRankAtColumnIndex:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "CalcRankAtColumnIndex",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(
        self: "CalcRankAtColumnIndex",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcRankAtColumnIndex",
        policy: "Policy",
        index: int,
        num_strata_deposited: typing.Optional[int],
    ) -> int:
        """After n strata have been deposited, what will the rank of the
        stratum at column index k be?

        Enables a HereditaryStratigraphicColumn using this predicate to
        optimize away storage of rank annotations on strata. Takes into the
        account the possiblity for in-progress stratum depositions that haven't
        been reflected in num_strata_deposited.
        """

        spec = policy.GetSpec()

        # allow index equal for in-progress deposition case
        assert (
            0
            <= index
            <= policy.CalcNumStrataRetainedExact(
                num_strata_deposited=num_strata_deposited,
            )
        )

        return next(
            rank
            for i, rank in enumerate(
                it.chain(
                    policy.IterRetainedRanks(num_strata_deposited),
                    # in-progress deposition case
                    (num_strata_deposited,),
                )
            )
            if i == index
        )
