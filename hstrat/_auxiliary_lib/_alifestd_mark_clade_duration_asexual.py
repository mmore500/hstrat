import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd

from ._alifestd_mark_max_descendant_origin_time_asexual import (
    alifestd_mark_max_descendant_origin_time_asexual,
)
from ._begin_prod_logging import begin_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_mark_clade_duration_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `clade_duration`, containing the difference between each the
    `origin_time` of each node and the maximum `origin_time` of its descendants.

    Leaf nodes will have duration 0.

    Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if "origin_time" not in phylogeny_df.columns:
        raise ValueError("phylogeny_df must contain `origin_time` column")

    if "max_descendant_origin_time" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_max_descendant_origin_time_asexual(
            phylogeny_df, mutate=True
        )

    phylogeny_df["clade_duration"] = (
        phylogeny_df["max_descendant_origin_time"].values
        - phylogeny_df["origin_time"].values
    )

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add column `clade_duration`, containing the difference between each node's `origin_time` and the maximum `origin_time` of its descendants.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_clade_duration_asexual",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    begin_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_mark_clade_duration_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_mark_clade_duration_asexual,
            ),
        )
