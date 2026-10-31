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
    assert getattr(dataframe, name) is getattr(build_trie, name)


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
