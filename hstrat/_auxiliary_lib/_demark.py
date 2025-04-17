from numbers import Number
import typing


def demark(object_: typing.Any) -> typing.Hashable:
    """Provide a hashable identifier for `object_`."""
    return object_ if isinstance(object_, (str, Number)) else id(object_)
