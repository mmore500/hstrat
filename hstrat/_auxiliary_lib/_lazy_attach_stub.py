from typing import Optional, Callable, Any

from lazy_loader import attach_stub


def lazy_attach_stub(
    __name: str,
    __file: str,
    *,
    launder: bool,
    launder_names: Optional[list[str]] = None
) -> tuple[Callable[[str], Any], Callable[[], list[str]], list[str]]:
    """
    An extension of the lazy_loader.attach_stub function.
    __name and __file is __name__ and __file__ (see how to call
    attach_stub: https://scientific-python.org/specs/spec-0001/).
    This drastically reduces load times for the library.

    If launder is True, the module name of an attr is set to the
    __name argument (see ._launder_impl_modules). If launder_names is
    given, then the attr is only launder if its name is in launder_names.

    Returns what you should name __getattr__, __dir__, and __all__
    """
    getattr__, dir__, all__ = attach_stub(__name, __file)
    if launder:

        def newgetattr__(n: str):
            attr = getattr__(n)
            if launder_names is not None and n not in launder_names:
                return attr
            try:
                attr.__module__ = __name
            except (AttributeError, TypeError):
                pass
            return attr

        return newgetattr__, dir__, all__
    return getattr__, dir__, all__
