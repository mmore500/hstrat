import typing

from ..PolicySpec import PolicySpec


class CalcMrcaUncertaintyRelUpperBoundPessimalRank:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: 'CalcMrcaUncertaintyRelUpperBoundPessimalRank',
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(
        self: 'CalcMrcaUncertaintyRelUpperBoundPessimalRank',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: 'CalcMrcaUncertaintyRelUpperBoundPessimalRank',
        policy: 'Policy',
        first_num_strata_deposited: int,
        second_num_strata_deposited: int,
    ) -> int:
        """Calculate rank for which upper bound on relative MRCA uncertainty is
        pessimized."""

        spec = policy.GetSpec()
        resolution = spec._guaranteed_mrca_recency_proportional_resolution

        if resolution == 0:
            least_last_rank = min(
                first_num_strata_deposited - 1,
                second_num_strata_deposited - 1,
            )
            return max(
                least_last_rank - 1,
                0
            )
        else:
            return 0
