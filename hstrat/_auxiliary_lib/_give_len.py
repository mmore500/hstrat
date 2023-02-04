import typing


def give_len(wrapee: typing.Iterable, len_: int) -> typing.Iterable:
    """Wrap an object to make Sized with `len(wrapee)` as provided `len_`."""

    # adapted from https://stackoverflow.com/a/2982
    class GiveLenWrapper:
        _wrapee: typing.Iterable

        def __init__(self: "GiveLenWrapper", wrapee: typing.Iterable) -> None:
            self._wrapee = wrapee

        # must define members inline or won't be recognized as wrapee etc.
        for attr in dir(wrapee):
            if attr not in {
                "__class__",
                "__delattr__",
                "__getattribute__",
                "__init__",
                "__name__",
                "__new__",
                "__qualname__",
                "__setattr__",
            }:
                exec(
                    f"""
{'@property' if not callable(getattr(wrapee, attr)) else ''}
def {attr}(self, *args, **kwargs):
    return self._wrapee.{attr}(*args, **kwargs)
                    """
                )

        def __len__(self: "GiveLenWrapper") -> int:
            return len_

    return GiveLenWrapper(wrapee)
