import typing

import opytional as opyt
import pandas as pd

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ._impl import build_tree_searchtable_python

try:
    from ._impl._build_tree_searchtable_cpp import build_tree_searchtable_cpp
except ImportError:
    build_tree_searchtable_cpp = None


def build_tree_searchtable(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    progress_wrap: typing.Optional[typing.Callable] = None,
    force_common_ancestry: bool = False,
    use_impl: typing.Literal["cpp", "python", None] = None,
) -> pd.DataFrame:
    """
    Uses the consolidated algorithm to build a tree, using a
    searchtable to access elements thereof.
    """

    try:
        build_tree_searchtable_impl = {
            "cpp": build_tree_searchtable_cpp,
            "either": opyt.or_value(
                build_tree_searchtable_cpp,
                build_tree_searchtable_python,
            ),
            "python": build_tree_searchtable_python,
        }[opyt.or_value(use_impl, "either")]
    except KeyError:
        raise ValueError(
            f"Invalid value {use_impl} for `use_impl`. "
            "Expected one of 'cpp', 'python', or None.",
        )

    if build_tree_searchtable_impl is None:
        raise ValueError(
            "build_tree_searchtable C++ impl was requested, but not available.",
        )

    return build_tree_searchtable_impl(
        population,
        taxon_labels,
        progress_wrap,
        force_common_ancestry,
    )
