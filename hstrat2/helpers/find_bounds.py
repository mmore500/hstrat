from functools import reduce
import operator
import typing

import opytional as opyt


def find_bounds(
    query: typing.Any,
    iterable: typing.Iterable[typing.Any],
    filter_below: typing.Callable = operator.lt,
    filter_above: typing.Callable = operator.gt,
    key: typing.Callable = lambda x: x,
    initializer: typing.Tuple[typing.Any, typing.Any] = (None, None),
) -> typing.Tuple[typing.Optional[typing.Any], typing.Optional[typing.Any]]:
    def operation(accumulation, element):
        cur_below, cur_above = accumulation

        element = key(element)
        maybe_below = element if filter_below(element, query) else None
        maybe_above = element if filter_above(element, query) else None

        res_below = opyt.apply_if_or_value(
            cur_below,
            lambda x: opyt.apply_if_or_value(
                maybe_below,
                lambda y: max(x, y),
                x,
            ),
            maybe_below,
        )
        res_above = opyt.apply_if_or_value(
            cur_above,
            lambda x: opyt.apply_if_or_value(
                maybe_above,
                lambda y: min(x, y),
                x,
            ),
            maybe_above,
        )

        return (res_below, res_above)

    return reduce(operation, iterable, initializer)
