import typing


def value_or(
    maybe_value: typing.Optional[typing.Any],
    fallback_value: typing.Any,
) -> typing.Any:
    if maybe_value is not None:
        return maybe_value
    else:
        return fallback_value
