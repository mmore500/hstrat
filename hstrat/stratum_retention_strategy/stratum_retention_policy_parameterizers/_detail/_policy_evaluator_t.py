import typing

policy_evaluator_t = typing.Callable[
    [typing.Type, int],
    typing.Union[float, int],
]
