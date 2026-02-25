import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_is_right_child_asexual import (
    alifestd_mark_is_right_child_asexual,
)
from ._alifestd_mark_num_leaves_asexual import alifestd_mark_num_leaves_asexual
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._begin_prod_logging import begin_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._jit import jit
from ._log_context_duration import log_context_duration


@jit(nopython=True)
def _alifestd_mark_num_preceding_leaves_asexual_fast_path(
    ancestor_ids: np.ndarray,
    num_leaves: np.ndarray,
    is_right_child: np.ndarray,
) -> np.ndarray:
    """Implementation detail for
    `alifestd_mark_num_preceding_leaves_asexual`."""

    num_preceding_leaves = np.zeros_like(ancestor_ids)
    for idx, ancestor_id in enumerate(ancestor_ids):
        num_preceding_leaves[idx] = (
            num_preceding_leaves[ancestor_id]
            + (num_leaves[ancestor_id] - num_leaves[idx]) * is_right_child[idx]
        )

    return num_preceding_leaves


def _alifestd_mark_num_preceding_leaves_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Implementation detail for
    `alifestd_mark_num_preceding_leaves_asexual`."""

    phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["num_preceding_leaves"] = 0

    for idx in phylogeny_df.index:
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        phylogeny_df.at[idx, "num_preceding_leaves"] = (
            phylogeny_df.at[ancestor_id, "num_preceding_leaves"]
            + (
                phylogeny_df.at[ancestor_id, "num_leaves"]
                - phylogeny_df.at[idx, "num_leaves"]
            )
            * phylogeny_df.at[idx, "is_right_child"]
        )

    return phylogeny_df


def alifestd_mark_num_preceding_leaves_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `num_preceding_leaves` with count of all leaves occuring
    before the present node in an inorder traversal.

    For internal nodes, the number of leaf nodes prior to the traversal of
    first (i.e., leftmost) descendant is marked.

    A topological sort will be applied if `phylogeny_df` is not topologically
    sorted. Dataframe reindexing (e.g., df.index) may be applied.

    Must be a strictly bifurcating tree.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly bifurcating")

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if "num_leaves" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_num_leaves_asexual(
            phylogeny_df, mutate=True
        )

    if "is_right_child" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_is_right_child_asexual(
            phylogeny_df, mutate=True
        )

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df[
            "num_preceding_leaves"
        ] = _alifestd_mark_num_preceding_leaves_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            phylogeny_df["num_leaves"].to_numpy(),
            phylogeny_df["is_right_child"].to_numpy(),
        )
        return phylogeny_df
    else:
        return _alifestd_mark_num_preceding_leaves_asexual_slow_path(
            phylogeny_df,
        )


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add column `num_preceding_leaves` with count of all leaves occurring before the present node in an inorder traversal.

Data is assumed to be in alife standard format.

Additional Notes
================
- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        allow_abbrev=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_parser_base(
        parser=parser,
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_num_preceding_leaves_asexual",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    begin_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_mark_num_preceding_leaves_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_mark_num_preceding_leaves_asexual,
            ),
        )
