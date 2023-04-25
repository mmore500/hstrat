import types
import typing


def launder_impl_modules(
    all_: typing.List[types.ModuleType], name: str
) -> None:
    """Stamp name into __module__ of items to hide implementation detail.

    Important for making the documentation work nice.
    """
    for item in all_:
        try:
            item.__module__ = name
        except (AttributeError, TypeError):
            pass
