import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_mark_num_descendants_asexual import (
    alifestd_mark_num_descendants_asexual,
)
from ._alifestd_mark_sister_asexual import alifestd_mark_sister_asexual
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_mark_clade_nodecount_ratio_sister_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `clade_nodecount_ratio_sister`, containing the ratio of each
    clade size to that of its sister.

    Root nodes will have ratio 1. Tree must be strictly bifurcating.

    Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly bifurcating")

    if "sister_id" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_sister_asexual(phylogeny_df, mutate=True)

    if "num_descendants" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_num_descendants_asexual(
            phylogeny_df, mutate=True
        )

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["clade_nodecount_ratio_sister"] = (
        phylogeny_df["num_descendants"].values + 1
    ) / (
        phylogeny_df.loc[phylogeny_df["sister_id"], "num_descendants"].values
        + 1
    )

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add column `clade_nodecount_ratio_sister`, containing the ratio of each clade size to that of its sister.

Data is assumed to be in alife standard format.

Additional Notes
================
- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_parser_base(
        parser=parser,
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_clade_nodecount_ratio_sister_asexual",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_mark_clade_nodecount_ratio_sister_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_mark_clade_nodecount_ratio_sister_asexual,
            ),
        )
