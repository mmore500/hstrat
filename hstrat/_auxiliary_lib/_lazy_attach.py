from typing import Any, Callable, Dict, List, Optional, Tuple

from lazy_loader import attach
import opytional as opyt


def lazy_attach(
    module_name: str,
    *,
    submodules: Optional[List[str]],
    submod_attrs: Optional[Dict[str, List[str]]],
    launder: bool,
    launder_names: Optional[List[str]] = None
) -> Tuple[Callable[[str], Any], Callable[[], List[str]], List[str]]:
    """
    Attaches lazy loading to a package to reduce load times by deferring
    loading of submodules and their attributes until needed. This is used
    throughout the project in when a package imports all attributes from
    a subpackage (otherwise, use _lazy_attach_stub.py). Called in the
    __init__.py file of the package.

    Parameters
    ----------
    module_name : str
        The name of the package in which symbols are being imported. This
        should be `__name__` to properly set up lazy loading.
    submodules : list of str
        A list of submodules within the package that are to be loaded lazily.
    submod_attrs : dict
        A dictionary where keys are submodule names and values are lists
        of attribute names within each submodule to be loaded in the namespace.
    launder : bool
        If True, the module name of an attribute is set to the `__name` argument.
        This allows for hiding implementation details of each class.
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
            Lists all available attributes, including lazily loaded ones.
        - `__all__` : list of str
            A list of all attributes for the namespace to be included in *
            imports and accessbile from other modules.

    Notes
    -----
    For more details on using `attach_lazy_loader`, refer to the
    Scientific Python project documentation:
    https://scientific-python.org/specs/spec-0001/

    This function leverages lazy loading to significantly reduce load
    times for large libraries by only loading submodules and attributes
    as they are accessed.

    See Also
    --------
    ._lazy_attach_stub : When there are no `__all__` imports, this function
        is preferred instead, as it only depends on a type stub.
    ._launder_impl_modules : Implementation details for laundering module
    names for attributes.
    """
    getattr__, dir__, all__ = lazy_loader.attach(
        module_name, submodules=submodules, submod_attrs=submod_attrs
    )
    if launder:

        def new_getattr(n: str) -> object:
            attr = getattr__(n)
            if apply_if(launder_names, lambda x: n not in x):
                return attr
            try:
                attr.__module__ = module_name
            except (AttributeError, TypeError):
                pass  # module attr not settable for all object types
            return attr

        return new_getattr, dir__, all__
    return getattr__, dir__, all__
