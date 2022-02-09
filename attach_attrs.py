import typing

def attach_attrs(
    attrs: typing.Dict[str, typing.Any,],
) -> typing.Callable[[typing.Callable,], typing.Callable,]:
    """Generates decorator that, when called, attaches `attrs` to a function."""

    # no need for @functools.wraps here
    def attach_attrs_decorator(
        f: typing.Callable,
    ) -> typing.Callable:
        """Attaches `attrs` to function `f` then returns `f`."""

        for k, v, in attrs.items():
            setattr(f, k, v,)
        return f

    return attach_attrs_decorator
