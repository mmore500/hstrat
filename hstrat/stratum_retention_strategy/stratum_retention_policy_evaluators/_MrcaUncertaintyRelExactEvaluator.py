import typing

import opytional as opyt

from ._detail import policy_param_focalizer_t


class MrcaUncertaintyRelExactEvaluator:
    """Enacts exact relative MRCA uncertainty parameterization requirement."""

    _at_num_strata_deposited: int
    _at_rank: typing.Optional[int]
    _policy_param_focalizer: policy_param_focalizer_t

    def __init__(
        self: "MrcaUncertaintyRelExactEvaluator",
        at_num_strata_deposited: int,
        at_rank: typing.Optional[int] = None,
        policy_param_focalizer: policy_param_focalizer_t = (
            lambda policy_t: lambda i: policy_t(i)
        ),
    ) -> None:
        """Initialize functor to evaluate exact relative MRCA uncertainty.

        Parameters
        ----------
        at_num_strata_deposited : int
            At what generation should we evaluate policy?
        at_rank : int, optional
            At what column position should we evaluate policy? If None, use
            pessimal position.
        policy_param_focalizer : callable
            Callable to create shim that constructs policy instance from
            parameter value. Default passes parameter value as sole argument to
            policy constructor.
        """
        self._at_num_strata_deposited = at_num_strata_deposited
        self._at_rank = at_rank
        self._policy_param_focalizer = policy_param_focalizer

    def __call__(
        self: "MrcaUncertaintyRelExactEvaluator",
        policy_t: typing.Type,
        parameter_value: int,
    ) -> float:
        """Get exact relative MRCA uncertainty under a specific parameter."""
        policy_factory = self._policy_param_focalizer(policy_t)
        policy = policy_factory(parameter_value)
        if self._at_rank is None:
            raise NotImplementedError(
                "CalcMrcaUncertaintyRelExactPessimalRank not yet implemented"
            )
        at_rank = opyt.or_value(
            self._at_rank,
            None,
            # policy.CalcMrcaUncertaintyRelExactPessimalRank(
            #     self._at_num_strata_deposited,
            #     self._at_num_strata_deposited,
            # ),
        )
        return policy.CalcMrcaUncertaintyRelExact(
            self._at_num_strata_deposited,
            self._at_num_strata_deposited,
            at_rank,
        )

    def __repr__(self: "MrcaUncertaintyRelExactEvaluator") -> str:
        return f"""{
            MrcaUncertaintyRelExactEvaluator.__qualname__
        }(at_num_strata_deposited={
            self._at_num_strata_deposited
        !r}, at_rank={
            self._at_rank
        !r}, policy_param_focalizer={
            self._policy_param_focalizer
        !r})"""

    def __str__(self: "MrcaUncertaintyRelExactEvaluator") -> str:
        title = "Exact Relative MRCA Uncertainty Evaluator"
        return f"""{
            title
        } (at num strata deposited: {
            self._at_num_strata_deposited
        }, at rank: {
            opyt.or_value(self._at_rank, 'pessimal')
        }, focalizer: {
            self._policy_param_focalizer
        })"""
