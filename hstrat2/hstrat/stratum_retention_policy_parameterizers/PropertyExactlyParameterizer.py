import sys
import typing

import interval_search as inch
import numpy as np
import opytional as opyt

from .PropertyAtLeastParameterizer import PropertyAtLeastParameterizer

_policy_evaluator_t = typing.Callable[
    [typing.Type, int],
    typing.Union[float, int],
]

class PropertyExactlyParameterizer:

    _impl: PropertyAtLeastParameterizer

    def __init__(
        self: 'PropertyExactlyParameterizer',
        target_value: typing.Union[float, int],
        policy_evaluator: _policy_evaluator_t,
        param_lower_bound: int=0,
        param_upper_bound: typing.Optional[int]=sys.maxsize,
    ) -> None:
        """Initialize functor to parameterize stratum retention policy so that
        an evaluated property is exactly equal to a target value.

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
        self._impl = PropertyAtLeastParameterizer(
            target_value=target_value,
            policy_evaluator=policy_evaluator,
            param_lower_bound=param_lower_bound,
            param_upper_bound=param_upper_bound,
        )

    def __call__(
        self: 'PropertyExactlyParameterizer',
        policy_t: typing.Type,
    ) -> typing.Optional['PolicySpec']:
        policy_factory = self._impl._policy_evaluator._policy_param_focalizer(
            policy_t,
        )
        try:
            res = self._impl._try_calc_parameter(policy_t)
            if res is not None:
                assert self._impl._param_lower_bound <= res
            if res is not None and self._impl._param_upper_bound is not None:
                assert res <= self._impl._param_upper_bound
        except (MemoryError, OverflowError, RecursionError):
            return None

        if (
            res is not None
            and self._impl._target_value == self._impl._policy_evaluator(
                policy_t,
                res,
            )
        ):
            return policy_factory(res).GetSpec()
        else:
            return None

    def __repr__(
        self: 'PropertyExactlyParameterizer',
    ) -> str:
        return f'''{
            PropertyExactlyParameterizer.__qualname__
        }(target_value={
            self._impl._target_value
        !r}, policy_evaluator={
            self._impl._policy_evaluator
        !r}, param_lower_bound={
            self._impl._param_lower_bound
        !r}, param_upper_bound={
            self._impl._param_upper_bound
        !r})'''

    def __str__(
        self: 'PropertyExactlyParameterizer',
    ) -> str:
        title = 'Exactly Parameterizer'
        return f'''{
            title
        } (target value: {
            self._impl._target_value
        }, evaluator: {
            self._impl._policy_evaluator
        }, param lower bound: {
            self._impl._param_lower_bound
        }, param upper bound: {
            opyt.or_value(self._impl._param_upper_bound, 'inf')
        })'''
