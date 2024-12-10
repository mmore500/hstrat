import re


def get_package_name(module_name: str) -> str:
    """
    Gets the package name given the fully qualified module name.

    Parameters
    ----------
    module_name : str
        The fully qualified module name, which usually should be `__name__`
    """
    return re.sub(r"\.[a-zA-Z0-9_]+$", "", module_name)
