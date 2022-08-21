import typing

from .._detail._PolicyCouplerBase import PolicyCouplerBase


class CalcMrcaUncertaintyAbsUpperBoundPessimalRankBruteForce:
    def __init__(
        self: "CalcMrcaUncertaintyAbsUpperBoundPessimalRankBruteForce",
        policy_spec: typing.Optional[typing.Any] = None,
    ) -> None:
        pass

    def __eq__(
        self: "CalcMrcaUncertaintyAbsUpperBoundPessimalRankBruteForce",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcMrcaUncertaintyAbsUpperBoundPessimalRankBruteForce",
        policy: typing.Optional[PolicyCouplerBase],
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
    ) -> int:
        """Calculate pessimal rank for upper bound on absolute MRCA
        uncertainty by brute force."""
        least_num_strata_deposited = min(
            first_num_strata_deposited,
            second_num_strata_deposited,
        )

        if least_num_strata_deposited == 0:
            return 0

        pessimal_rank = max(
            (
                (
                    r,
                    policy.CalcMrcaUncertaintyAbsUpperBound(
                        first_num_strata_deposited,
                        second_num_strata_deposited,
                        r,
                    ),
                )
                for r in range(least_num_strata_deposited)
            ),
            key=lambda tup: tup[1],
        )[0]

        return pessimal_rank
