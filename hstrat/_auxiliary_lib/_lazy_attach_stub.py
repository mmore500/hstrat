from typing import Optional, Callable, Any, List

from lazy_loader import attach_stub


def lazy_attach_stub(
    module_name: str,
    module_path: str,
    *,
    launder: bool,
    launder_names: Optional[List[str]] = None
) -> tuple[Callable[[str], Any], Callable[[], List[str]], List[str]]:
    """
    Attaches a lazy loading stub to a package, enabling deferred loading
    of submodules and attributes to improve load times. This is used by
    importing necessary functions in a type stub and using said stub to
    determine how to lazily load attributes.

    Parameters
    ----------
    module_name : str
        The name of the main package. This should be `__name__` to properly
        set up the lazy loading stub.
    module_path : str
        The file path of the main module. This should be `__file__` to ensure
        correct module referencing.
    launder : bool, optional
        If True, the module name of an attribute is set to the `module_name`
        argument, effectively renaming it in the namespace to hide implementation
        details. Default is False.
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
            A list of all attributes in the namespace, allowing for
            import by other modules.

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
        where submodules and attributes are loaded directly into the
        namespace.
    ._launder_impl_modules : Implements laundering for module names
    in attributes.
    """
    getattr__, dir__, all__ = attach_stub(module_name, module_path)
    if launder:

        def newgetattr__(n: str):
            attr = getattr__(n)
            if launder_names is not None and n not in launder_names:
                return attr
            try:
                attr.__module__ = module_name
            except (AttributeError, TypeError):
                pass
            return attr

        return newgetattr__, dir__, all__
    return getattr__, dir__, all__
