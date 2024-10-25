import os
import ast
import importlib

def find_modules_with_all_references(file: str):
    """
    Parses the given source code using the AST module to find all modules listed
    in `submod_attrs` that reference `__all__`.

    Args:
        source_code (str): The Python source code to analyze.

    Returns:
        list: A list of modules from `submod_attrs` that reference `__all__`.
    """
    modules_with_all = []

    with open(file, 'r') as f:
        source_code = f.read()
    tree = ast.parse(source_code)

    for node in tree.body:
        if (isinstance(node, ast.Assign)
            and isinstance(call_node := node.value, ast.Call)
            and isinstance(call_node.func, ast.Name)
            and call_node.func.id == 'lazy_attach'
        ):
            for keyword in call_node.keywords:
                if keyword.arg == 'submod_attrs' and isinstance(keyword.value, ast.Dict):
                    submod_attrs_dict = keyword.value
                    for key_node, value_node in zip(
                        submod_attrs_dict.keys, submod_attrs_dict.values
                    ):
                        if not isinstance(key_node, ast.Constant):
                            continue
                        module_name = key_node.value
                        if (isinstance(value_node, ast.Attribute)
                            and value_node.attr == '__all__'
                            and isinstance(value_node.value, ast.Name)
                            and module_name == value_node.value.id
                        ):
                            modules_with_all.append(module_name)
    return modules_with_all

def get_all_from_stub(file_path) -> list[str]:
    with open(file_path, "r") as file:
        file_content = file.read()

    tree = ast.parse(file_content)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, ast.List):
                        return [elt.s for elt in node.value.elts if isinstance(elt, ast.Constant)]

    raise Exception("__all__ could not be found")

def check_packages(package: list[str]) -> None:
    package_path = os.path.join(*package)
    subpackages = find_modules_with_all_references(os.path.join(package_path, '__init__.py'))
    for subpkg in subpackages:
        check_packages(package + [subpkg])
        symbols = get_all_from_stub(os.path.join(package_path, subpkg, '__init__.pyi'))
        mod = importlib.import_module('.'.join(package + [subpkg]))
        assert sorted(mod.__all__) == sorted(symbols), f"Error with {'.'.join(package)}"
    for subdir in os.listdir(package_path):
        if (subdir not in subpackages and os.path.isdir(os.path.join(package_path, subdir))
            and '__init__.py' in os.listdir(os.path.join(package_path, subdir))):
            check_packages(package + [subdir])

check_packages(['hstrat'])
