def get_package_name(qual_name: str) -> str:
    """
    Gets the package name given the fully qualified module name.

    Examples
    --------
    >>> get_package_name("baz")
    ''
    >>> get_package_name("foo.bar")
    'foo'

    Parameters
    ----------
    qual_name : str
        The fully qualified module name, which usually should be `__name__`
    """
    *package_names, _module_name = qual_name.split(".")
    return ".".join(package_names)
