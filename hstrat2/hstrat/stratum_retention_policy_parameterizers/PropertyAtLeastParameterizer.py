import interval_search as inch
import numpy as np
import opytional as opyt
import sys
import typing


_policy_evaluator_t = typing.Callable[
    [typing.Type, int],
    typing.Union[float, int],
]

class PropertyAtLeastParameterizer:

    _policy_evaluator: _policy_evaluator_t
    _param_lower_bound: int
    _param_upper_bound: typing.Optional[int]

    def __init__(
        self: 'PropertyAtLeastParameterizer',
        target_value: typing.Union[float, int],
        policy_evaluator: _policy_evaluator_t,
        param_lower_bound: int=0,
        param_upper_bound: typing.Optional[int]=sys.maxsize,
    ) -> None:
        """Initialize functor to parameterize stratum retention policy so that
        an evaluated property is greater than or equal to a target value.

        Parameters
        ----------
        target_value : float or int
            The threshold property value to parameterize the policy to meet.
        policy_evaluator : int
            Functor that evaluates a policy at a particular parameter value.
        param_lower_bound : int
            Lower value on the range of parameter values to search, inclusive.
        param_upper_bound : int, optional
            Upper bound on the range of parameter values to search, inclusive.
            If None, no upper bound is used.
        """
        self._target_value = target_value
        self._policy_evaluator = policy_evaluator
        self._param_lower_bound = param_lower_bound
        self._param_upper_bound = param_upper_bound

    def __call__(
        self: 'PropertyAtLeastParameterizer',
        policy_t: typing.Type,
    ) -> typing.Optional['PolicySpec']:
        policy_factory = self._policy_evaluator._policy_param_focalizer(
            policy_t,
        )
        try:
            return opyt.apply_if(
                self._try_calc_parameter(policy_t),
                lambda x: policy_factory(x).GetSpec(),
            )
        except (MemoryError, OverflowError, RecursionError):
            return None

    def _try_calc_parameter(
        self: 'PropertyAtLeastParameterizer',
        policy_t: typing.Type,
    ) -> typing.Optional[int]:
        lb = self._param_lower_bound
        ub = self._param_upper_bound
        thresh = self._target_value
        eval_at_param = lambda val: self._policy_evaluator(policy_t, val)

        next_diff_param = inch.interval_search(
            lambda p: eval_at_param(p) != eval_at_param(lb),
            lower_bound=lb,
            upper_bound=ub,
        )
        sign = opyt.apply_if(
            next_diff_param,
            lambda x: np.sign(eval_at_param(x) - eval_at_param(lb))
        )
        assert sign != 0

        if sign is None or sign == 1:
            # if all parameters in search range evaluate to same value
            # (sign is None) or values increase with parameter (sign == 1)
            # forward search for parameter, if any, that satisfies
            # parameterization requirement
            return inch.interval_search(
                lambda p: eval_at_param(p) >= thresh,
                lower_bound=lb,
                upper_bound=ub,
            )
        elif eval_at_param(lb) >= thresh:
            # if value decreases with parameter and the lowest value satisfies
            # parameterization requirement, forward search for last parameter
            # that satisfies parameterization requirement
            assert sign == -1
            try:
                res = inch.interval_search(
                    # successor fails requirement
                    lambda p: eval_at_param(p + 1) < thresh,
                    lower_bound=lb,
                    upper_bound=opyt.apply_if(ub, lambda x: x - 1),
                )
                if res is not None:
                    return res
            except (MemoryError, OverflowError, RecursionError):
                pass
            # looking for parameter with successor that fails requirement
            # failed
            # try again, looking for any parameter that minimally satisfies
            # requirement
            try:
                res = inch.interval_search(
                    lambda p: eval_at_param(p) == thresh,
                    lower_bound=lb,
                    upper_bound=ub,
                )
                if res is not None:
                    return res
            except (MemoryError, OverflowError, RecursionError):
                pass
            # all searchable parameters sastisfy requirement, so
            # arbitrarily pick lower bound
            return sys.maxsize
        else:
            assert sign == -1
            assert eval_at_param(lb) < thresh
            return None

    def __repr__(
        self: 'PropertyAtLeastParameterizer',
    ) -> str:
        return f'''{
            PropertyAtLeastParameterizer.__qualname__
        }(target_value={
            self._target_value
        !r}, policy_evaluator={
            self._policy_evaluator
        !r}, param_lower_bound={
            self._param_lower_bound
        !r}, param_upper_bound={
            self._param_upper_bound
        !r})'''

    def __str__(
        self: 'PropertyAtLeastParameterizer',
    ) -> str:
        title = 'At Least Parameterizer'
        return f'''{
            title
        } (target value: {
            self._target_value
        }, evaluator: {
            self._policy_evaluator
        }, param lower bound: {
            self._param_lower_bound
        }, param upper bound: {
            opyt.value_or(self._param_upper_bound, 'inf')
        })'''
