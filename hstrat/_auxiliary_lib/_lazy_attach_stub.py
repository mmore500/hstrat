from typing import Any, Callable, List, Tuple

import lazy_loader

from ._GetAttrLaunderShim import GetAttrLaunderShim


def lazy_attach_stub(
    module_name: str,
    module_path: str,
    *,
    should_launder: Callable = lambda _: True,
) -> Tuple[Callable[[str], Any], Callable[[], List[str]], List[str]]:
    """
    Attaches a lazy loading stub to a package, enabling deferred loading
    of submodules and attributes to improve load times. Used by importing
    necessary symbols into a type stub (a .pyi file) and evaluating said
    type stub to determine symbols to import. Called in the __init__.py
    file of a package, assuming there exists an __init__.pyi file too.

    Parameters
    ----------
    module_name : str
        The name of the package in which symbols are being imported. This
        should be `__name__` to properly set up the lazy loading stub.
    module_path : str
        The file path of the main module. This should be `__file__` to ensure
        correct module referencing.
    should_launder : callable, default `lambda x: True`
        A callable that takes a string attr and returns a boolean indicating
        whether the attr should be laundered. If True, __module__ on the
        attr will attempt to be set to `module_name`.

    Returns
    -------
    tuple
        A tuple containing the items needed to define `__getattr__`, `__dir__`,
        and `__all__` in the main module:

        - `__getattr__` : function
            Retrieves attributes lazily as needed.
        - `__dir__` : function
            Lists all available attributes, including those lazily loaded.
        - `__all__` : list of str
            A list of all attributes for the namespace to be included in *
            imports and accessbile from other modules.

    Notes
    -----
    This function relies on the lazy loading mechanism provided by
    `attach_stub` to minimize initial load times for large libraries by
    delaying the loading of specific modules and attributes until they
    are accessed.

    For additional usage information, refer to the Scientific Python
    project documentation:
    https://scientific-python.org/specs/spec-0001/

    See Also
    --------
    ._lazy_attach : Provides an alternative lazy loading method,
        where submodules and attributes are declared directly in the
        __init__.py file. This was used where `__all__` imports are forwarded from
        subpackages, as lazy_loader does not support that natively.
    ._launder_impl_modules : Implements laundering for module names
    in attributes.
    """
    getattr__, dir__, all__ = lazy_loader.attach_stub(module_name, module_path)
    wrapped_getattr = GetAttrLaunderShim(
        getattr__, should_launder, module_name
    )
    return wrapped_getattr, dir__, all__
