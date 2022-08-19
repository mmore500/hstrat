import typing

from ..stratum_retention_policies._detail import PolicyCouplerBase

_policy_param_focalizer_t = typing.Callable[
    [typing.Type],
    typing.Callable[[int], PolicyCouplerBase],
]
