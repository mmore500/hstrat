#!/usr/bin/env python3
"""
Script to validate and analyze Python packages for correct use of `__all__` references
across modules and type stubs. Uses the AST module to parse source code for compliance
with lazy-loading and `__all__` reference conventions. The requirements are as follows:
1) In an __init__.py file where the __all__ of some subpackage is accessed, the type stub
    of said subpackage must declare an __all__ equivalent to the actual (evaluated) __all__.
2) Every symbol imported from the __all__ of a subpackage must be in the __all__ of the
    type stub of the main package.

Functions
---------
find_modules_with_all_references(file_path)
    Parses a source file to find all modules listed in `submod_attrs`
    that reference `__all__`.

get_dunder_all_from_stub(file_path)
    Extracts the `__all__` list from a specified type stub file (`.pyi`).

check_accurate_all_imports(package)
    Recursively checks packages and sub-packages to ensure that all symbols
    referenced in `__all__` in each subpackage are consistent with the symbols
    specified in type stubs and available in imports.
"""

import ast
import importlib
import os
from pathlib import Path
from typing import List


def find_modules_with_all_references(file_path: str):
    """
    Parses the given source code using the AST module to find all modules listed
    in `submod_attrs` that reference `__all__`.

    Parameters
    ----------
    file_path : str
        The file path of the Python source file to analyze.

    Returns
    -------
    list of str
        A list of module names from `submod_attrs` that reference `__all__`.

    Notes
    -----
    The function uses the `ast` module to parse the source file and identify
    assignments that contain a `lazy_attach` call with a `submod_attrs` dictionary,
    where module names are specified with a `__all__` reference.
    """
    modules_with_all = []
    tree = ast.parse(Path(file_path).read_text())
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(call_node := node.value, ast.Call)
            and isinstance(call_node.func, ast.Name)
            and call_node.func.id == "lazy_attach"
        ):
            for keyword in call_node.keywords:
                if keyword.arg == "submod_attrs" and isinstance(
                    keyword.value, ast.Dict
                ):
                    submod_attrs_dict = keyword.value
                    for key_node, value_node in zip(
                        submod_attrs_dict.keys, submod_attrs_dict.values
                    ):
                        if not isinstance(key_node, ast.Constant):
                            continue
                        module_name = key_node.value
                        if (
                            isinstance(value_node, ast.Attribute)
                            and value_node.attr == "__all__"
                            and isinstance(value_node.value, ast.Name)
                            and module_name == value_node.value.id
                        ):
                            modules_with_all.append(module_name)
    return modules_with_all


def get_dunder_all_from_stub(file_path: str) -> List[str]:
    """
    Extracts the `__all__` symbols from a type stub (`.pyi`) file.

    Parameters
    ----------
    file_path : str
        The file path of the type stub file to parse.

    Returns
    -------
    list of str
        A list of symbols defined in `__all__` in the type stub.

    Raises
    ------
    Exception
        If `__all__` could not be found in the specified file.

    Notes
    -----
    This function specifically looks for assignments to `__all__` in the type
    stub file and returns a list of the symbols declared in it.
    """
    tree = ast.parse(Path(file_path).read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, ast.List):
                        return [
                            elt.s
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant)
                        ]

    raise Exception("__all__ could not be found")


def check_accurate_all_imports(package: List[str]) -> List[str]:
    """
    Recursively checks all subpackages in a given package to ensure that `__all__`
    symbols in type stubs are consistent with imported symbols.

    Parameters
    ----------
    package : list of str
        The list representing the package hierarchy to check. The root package
        name is the first element.

    Returns
    -------
    list of str
        A list of violations that can be printed after done.

    Notes
    -----
    This function ensures consistency between type stubs (`.pyi` files) and
    actual modules by verifying that symbols in `__all__` match across both.
    It imports each subpackage to check the presence of expected attributes.

    See Also
    --------
    find_modules_with_all_references : Identifies modules referencing `__all__`
        in their `submod_attrs` dictionaries.
    get_dunder_all_from_stub : Extracts `__all__` from type stubs.
    """
    violations = []
    package_path = os.path.join(*package)
    subpackages = find_modules_with_all_references(
        os.path.join(package_path, "__init__.py")
    )
    native_all_symbols = (
        get_dunder_all_from_stub(os.path.join(package_path, "__init__.pyi"))
        if subpackages
        else []
    )
    for subpkg in subpackages:
        check_accurate_all_imports(package + [subpkg])
        symbols = get_dunder_all_from_stub(
            os.path.join(package_path, subpkg, "__init__.pyi")
        )
        for s in symbols:
            if not s in native_all_symbols:
                violations.append(f"Symbol {s} from '{subpkg}' was imported by {'.'.join(package)} but not referenced in its __all__")
        mod = importlib.import_module(".".join(package + [subpkg]))
        if not sorted(mod.__all__) == sorted(symbols):
            violations.append(f"Error with {'.'.join(package + [subpkg])}: type stub __all__ is inconsistent")
    for subdir in os.listdir(package_path):
        if (
            subdir not in subpackages
            and os.path.isdir(os.path.join(package_path, subdir))
            and "__init__.py" in os.listdir(os.path.join(package_path, subdir))
        ):
            check_accurate_all_imports(package + [subdir])
    return violations

if __name__ == "__main__":
    cutoff_index = __file__.find("hstrat") + len("hstrat")  # first instance should be root directory
    os.chdir(__file__[:cutoff_index])
    violations = check_accurate_all_imports(["hstrat"])
    if not violations:
        exit(0)
    for violation in violations:
        print(f"ERROR: {violation }")
    raise Exception("Violations were found")
