import typing

_policy_param_focalizer_t = typing.Callable[
    [typing.Type],
    typing.Callable[[int], "Policy"],
]


class NumStrataRetainedExactPolicyEvaluator:

    _at_num_strata_deposited: int
    _policy_param_focalizer: _policy_param_focalizer_t

    def __init__(
        self: "NumStrataRetainedExactPolicyEvaluator",
        at_num_strata_deposited: int,
        policy_param_focalizer: _policy_param_focalizer_t = lambda policy_t: lambda i: policy_t(
            i
        ),
    ) -> None:
        """Initialize functor to evaluate exact num strata retained.

        Parameters
        ----------
        at_num_strata_deposited : int
            At what generation should we evaluate policy?
        policy_param_focalizer : callable
            Callable to create shim that constructs policy instance from
            parameter value. Default passes parameter value as sole argument to
            policy constructor.
        """
        self._at_num_strata_deposited = at_num_strata_deposited
        self._policy_param_focalizer = policy_param_focalizer

    def __call__(
        self: "NumStrataRetainedExactPolicyEvaluator",
        policy_t: typing.Type,
        parameter_value: int,
    ) -> int:
        """Evaluate exact num strata retained for policy with a particular
        parameter value."""
        policy_factory = self._policy_param_focalizer(policy_t)
        policy = policy_factory(parameter_value)
        return policy.CalcNumStrataRetainedExact(
            self._at_num_strata_deposited,
        )

    def __repr__(
        self: "NumStrataRetainedExactPolicyEvaluator",
    ) -> str:
        return f"""{
            NumStrataRetainedExactPolicyEvaluator.__qualname__
        }(at_num_strata_deposited={
            self._at_num_strata_deposited
        !r}, policy_param_focalizer={
            self._policy_param_focalizer
        !r})"""

    def __str__(
        self: "NumStrataRetainedExactPolicyEvaluator",
    ) -> str:
        title = "Exact Num Strata Retained Evaluator"
        return f"""{
            title
        } (at num strata deposited: {
            self._at_num_strata_deposited
        }, focalizer: {
            self._policy_param_focalizer
        })"""
