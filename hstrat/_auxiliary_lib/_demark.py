from numbers import Number
import typing


def demark(object: typing.Any) -> int:
    """Provide a hashable identifier for `object`."""
    return object if isinstance(object, (str, Number)) else id(object)
