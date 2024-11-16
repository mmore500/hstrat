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
find_modules_with_all_references(package_path)
    Parses a the `__init__.py` in the `package_path` to find all subpackages from which
    all symbols are imported (via `__all__`).

get_dunder_all_from_stub(package_path)
    Extracts the `__all__` list from the `__init__.pyi` file in the `package_path`.

check_accurate_all_declarations()
    Walks the `hstrat` directory and makes sure that the `__all__` defined in a type stub
    of a package is the same as the `__all__` obtained by importing the package directly.
    Returns a generator of violations.

check_accurate_subpackage_star_imports()
    If a package imports `__all__` from a subpackages, makes sure that that subpackage's
    real `__all__` is a subset of the `__all__` declared in the type stub of the importing
    package. Returns a generator of violations.

check_accurate_flat_namespace()
    Checks the flat namespace `hstrat.hstrat` and assures that the `__all__` defined in its
    `__init__.pyi` is accurate, containing all symbols from flattened submodules.
"""

import ast
import importlib.util
import os
from pathlib import Path
from types import ModuleType
from typing import Iterable, List


def module_name_from_path(path: str) -> str:
    return path.replace(os.path.sep, ".")


def import_from_path(directory_path) -> ModuleType:
    """Import a module from a specified directory path."""
    module_name = module_name_from_path(directory_path)
    spec = importlib.util.spec_from_file_location(
        module_name, os.path.join(directory_path, "__init__.py")
    )
    assert (
        spec is not None and spec.loader is not None
    ), f"Module '{module_name}' was not found."
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_modules_with_all_references(package_path: str) -> list:
    """
    Parses the `__init__.py` file of the given package path using the
    AST module to find all imports of subpackages that reference `__all__`.

    Parameters
    ----------
    package_path : str
        The file path of the Python package to analyze.

    Returns
    -------
    list of str
        A list of module names from `submod_attrs` that reference `__all__`.

    Notes
    -----
    The function uses the `ast` module to parse the source file and identify
    assignments that contain a `lazy_attach` call with a `submod_attrs` dictionary,
    where module names are specified with an `__all__` reference.
    """
    modules_with_all = []
    tree = ast.parse((Path(package_path) / "__init__.py").read_text())
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


def get_dunder_all_from_stub(package_path: str) -> List[str]:
    """
    Extracts the `__all__` symbols from a type stub (`.pyi`) file,
    given a path to the package containing it.

    Parameters
    ----------
    package_path : str
        The file path of package of the type stub file to parse.

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
    tree = ast.parse((Path(package_path) / "__init__.pyi").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, ast.List):
                        return [
                            element.s
                            for element in node.value.elts
                            if isinstance(element, ast.Constant)
                        ]

    raise Exception("__all__ could not be found")


def get_eligible_package_paths() -> Iterable[str]:
    """
    Traverses the `hstrat` package directory and returns
    the path for every directory that contains an `__init__.pyi`,
    as these are the valid packages to run the following checks on.
    """
    for path, _, files in os.walk("hstrat"):
        if "__init__.pyi" in files:
            yield path


def _symbol_not_in_stub(mod_path: str, sym: str):
    """
    Helper function for below to format a message in the case where
    a symbol defined in the `__all__` of a module is not in the type stub.
    """
    return f"Package '{module_name_from_path(mod_path)}' includes '{sym}' but does not declare it in the type stub."


def _symbol_not_in_module(mod_path: str, sym: str):
    """
    Helper function for below to format a message in the case where
    a symbol defined in the `__all__` of a type stub is not in the module.
    """
    return f"Type stub for '{module_name_from_path(mod_path)}' declares '__all__' that contains '{sym}' while the package itself does not contain it."


def check_accurate_all_declarations() -> Iterable[str]:
    """
    Check that the `__all__` from a package is the same as that
    defined in the type stub. Does this by reading the `__all__`
    from the type stub, and comparing it an `__all__` imported
    directly from the package.
    """
    for path in get_eligible_package_paths():
        type_stub_all = set(get_dunder_all_from_stub(path))
        module_all = set(getattr(import_from_path(path), "__all__"))
        for sym in type_stub_all - module_all:
            yield _symbol_not_in_module(path, sym)
        for sym in module_all - type_stub_all:
            yield _symbol_not_in_stub(path, sym)


def check_accurate_subpackage_star_imports() -> Iterable[str]:
    """
    If a package imports `__all__` from a subpackages, makes sure that
    that subpackage's real `__all__` is a subset of the `__all__` declared
    in the type stub of the importing package.
    """
    for path in get_eligible_package_paths():
        type_stub_all = get_dunder_all_from_stub(path)
        for subpackage in find_modules_with_all_references(path):
            subpackage_all = getattr(
                import_from_path(os.path.join(path, subpackage)), "__all__"
            )
            for sym in set(subpackage_all) - set(type_stub_all):
                yield f"Type stub for '{module_name_from_path(path)}' declares '__all__' that does not contain symbol '{sym}' from subpackage '{subpackage}'."


def check_accurate_flat_namespace() -> Iterable[str]:
    """
    Checks the flat namespace `hstrat.hstrat` and assures
    that the `__all__` defined in its `__init__.pyi` is accurate,
    containing all symbols from flattened submodules.
    """
    type_stub_all = get_dunder_all_from_stub(os.path.join("hstrat", "hstrat"))
    for subpackage in os.listdir("hstrat"):
        if (
            subpackage != "hstrat"
            and not subpackage.startswith("_")
            and (
                os.path.exists(
                    os.path.join("hstrat", subpackage, "__init__.pyi"),
                )
            )
        ):
            subpackage_all = getattr(
                import_from_path(os.path.join("hstrat", subpackage)), "__all__"
            )
            for sym in set(subpackage_all) - set(type_stub_all):
                yield f"Type stub for flat namespace 'hstrat.hstrat' does not contain symbol '{sym}' from '{subpackage}'."


if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent.parent.resolve())
    violations = [
        *check_accurate_all_declarations(),
        *check_accurate_subpackage_star_imports(),
        *check_accurate_flat_namespace(),
    ]
    print(f"{len(violations)} violations found.")
    for v in violations:
        print(v)

    exit_code = len(violations) > 0
    exit(exit_code)
