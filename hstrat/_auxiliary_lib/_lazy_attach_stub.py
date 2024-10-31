from typing import Any, Callable, List, Optional, Tuple

import lazy_loader
import opytional as opyt


def lazy_attach_stub(
    module_name: str,
    module_path: str,
    *,
    launder: bool,
    launder_names: Optional[List[str]] = None
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
    launder : bool
        If True, the `__module__` of an attribute is set to the `module_name`
        argument, effectively renaming it upon access to hide implementation
        details.
    launder_names : list of str, optional
        A list of attribute names to launder, if `launder` is True. Only
        attributes in this list will have their names laundered. If None,
        all attributes are laundered. Default is None.

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
        __init__.py file. This was used when there were `__all__` imports
        from some subpackage, as lazy_loader does not support that.
    ._launder_impl_modules : Implements laundering for module names
    in attributes.
    """
    getattr__, dir__, all__ = lazy_loader.attach_stub(module_name, module_path)
    if launder:

        def new_getattr(n: str):
            attr = getattr__(n)
            if opyt.apply_if(launder_names, lambda x: n not in x):
                return attr
            try:
                attr.__module__ = module_name
            except (AttributeError, TypeError):
                pass  # module attr not settable for all object types
            return attr

        return new_getattr, dir__, all__
    return getattr__, dir__, all__
