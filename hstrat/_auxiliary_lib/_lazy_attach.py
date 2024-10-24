from typing import Callable, Optional, Any

from lazy_loader import attach


def lazy_attach(
    __name: str, *,
    submodules: Optional[list[str]], submod_attrs: Optional[dict[str, list[str]]],
    launder: bool, launder_names: Optional[list[str]] = None
) -> tuple[Callable[[str], Any], Callable[[], list[str]], list[str]]:
    """
    An extension of the lazy_loader.attach function. __name is
    __name__ (see how to call attach:
    https://scientific-python.org/specs/spec-0001/).

    submodules are the list of submodules in the package, while submod_attrs
    are the attributes in said submodule to be loaded in a flat namespace.
    This drastically reduces load times for the library.

    If launder is True, the module name of an attr is set to the
    __name argument (see ._launder_impl_modules). If launder_names is given,
    then an attr is only laundered if its name is in launder_names.

    Returns what you should name __getattr__, __dir__, and __all__
    """
    getattr__, dir__, all__ = attach(__name, submodules=submodules, submod_attrs=submod_attrs)
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
