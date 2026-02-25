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
from ._begin_prod_logging import begin_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._jit import jit
from ._log_context_duration import log_context_duration


@jit(nopython=True)
def _alifestd_get_ancestor_origin_time_asexual_contiguous(
    ancestor_ids: np.ndarray,
    origin_times: np.ndarray,
) -> np.ndarray:
    """Optimized implementation for asexual phylogenies with contiguous ids."""
    ancestor_ids = ancestor_ids.astype(np.uint64)
    ancestor_origin_times = np.empty_like(origin_times)

    for id_, _ in enumerate(ancestor_ids):
        ancestor_id = ancestor_ids[id_]
        ancestor_origin_time = origin_times[ancestor_id]
        ancestor_origin_times[id_] = ancestor_origin_time

    return ancestor_origin_times


def alifestd_mark_ancestor_origin_time_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `ancestor_origin_time`.

    Dataframe must provide column `origin_time`.

    A topological sort will be applied if `phylogeny_df` is not topologically
    sorted. Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if "origin_time" not in phylogeny_df.columns:
        raise ValueError("Column 'origin_time' not found in dataframe.")

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df) and not phylogeny_df.empty:
        # optimized implementation for contiguous ids
        phylogeny_df[
            "ancestor_origin_time"
        ] = _alifestd_get_ancestor_origin_time_asexual_contiguous(
            phylogeny_df["ancestor_id"].values,
            phylogeny_df["origin_time"].values,
        )
        return phylogeny_df

    # slower fallback implementation
    phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["ancestor_origin_time"] = phylogeny_df["origin_time"].copy()

    for idx in reversed(phylogeny_df.index):
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        ancestor_origin_time = phylogeny_df.at[ancestor_id, "origin_time"]
        phylogeny_df.at[idx, "ancestor_origin_time"] = ancestor_origin_time

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add column `ancestor_origin_time`.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_ancestor_origin_time_asexual",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    begin_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_mark_ancestor_origin_time_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_mark_ancestor_origin_time_asexual,
            ),
        )
