import importlib

import pytest

from hstrat._auxiliary_lib import ExperimentalWarning

from ._origin_time_testing import make_population


@pytest.mark.parametrize(
    "package",
    ["build_trie_crosspair", "build_trie_upgma", "build_brute_upgma"],
)
def test_surface_build_tree_warns_experimental(package: str):
    module = importlib.import_module(f"hstrat.dataframe.{package}")
    with pytest.warns(ExperimentalWarning, match="is experimental"):
        module.surface_build_tree(make_population().head(4))


def test_build_trie_not_experimental():
    import warnings

    from hstrat.dataframe.build_trie import surface_build_tree

    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always")
        surface_build_tree(make_population().head(4))
    assert not any(issubclass(w.category, ExperimentalWarning) for w in record)
