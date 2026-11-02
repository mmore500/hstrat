import subprocess

import pytest

from hstrat import dataframe
from hstrat.dataframe import build_trie


@pytest.mark.parametrize(
    "name",
    [
        "surface_build_tree",
        "surface_build_tree_over",
        "surface_postprocess_trie",
        "surface_test_drive",
        "surface_unpack_reconstruct",
        "surface_validate_trie",
    ],
)
def test_top_level_aliases(name: str):
    # resolve via lazy loaders, as importing a same-named CLI submodule
    # (e.g., in other tests) rebinds the package attribute to the module
    assert dataframe.__getattr__(name) is build_trie.__getattr__(name)
    assert callable(dataframe.__getattr__(name))


@pytest.mark.parametrize(
    "module",
    [
        "surface_build_tree",
        "surface_build_tree_over",
        "surface_postprocess_trie",
        "surface_test_drive",
        "surface_unpack_reconstruct",
        "surface_validate_trie",
    ],
)
def test_cli_help(module: str):
    subprocess.run(  # nosec B603
        ["python3", "-m", f"hstrat.dataframe.build_trie.{module}", "--help"],
        check=True,
    )
