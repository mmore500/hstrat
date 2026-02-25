import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._jit import jit
from ._log_context_duration import log_context_duration


@jit(nopython=True)
def _alifestd_calc_node_depth_asexual_contiguous(
    ancestor_ids: np.ndarray,
) -> np.ndarray:
    """Optimized implementation for asexual phylogenies with contiguous ids."""
    ancestor_ids = ancestor_ids.astype(np.uint64)
    node_depths = np.full_like(ancestor_ids, -1, dtype=np.int64)

    for id_, _ in enumerate(ancestor_ids):
        ancestor_id = ancestor_ids[id_]
        ancestor_depth = node_depths[ancestor_id]
        node_depths[id_] = ancestor_depth + 1

    return node_depths


def alifestd_mark_node_depth_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `node_depth`, counting the number of nodes between a node
    and the root.

    A topological sort will be applied if `phylogeny_df` is not topologically
    sorted. Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        # optimized implementation for contiguous ids
        node_depths = _alifestd_calc_node_depth_asexual_contiguous(
            phylogeny_df["ancestor_id"].values,
        )
        phylogeny_df["node_depth"] = node_depths
        return phylogeny_df

    # slower fallback implementation
    phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["node_depth"] = -1

    for idx in phylogeny_df.index:
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        ancestor_depth = phylogeny_df.at[ancestor_id, "node_depth"]
        phylogeny_df.at[idx, "node_depth"] = ancestor_depth + 1

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add column `node_depth`, counting the number of nodes between a node and the root.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_node_depth_asexual",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()
    logging.info("hstrat version %s", get_hstrat_version())

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_mark_node_depth_asexual", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_mark_node_depth_asexual,
            ),
        )
