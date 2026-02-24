import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd

from ._alifestd_mark_roots import alifestd_mark_roots
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_mark_oldest_root(
    phylogeny_df: pd.DataFrame, mutate: bool = False
) -> pd.DataFrame:
    """Point all other roots to oldest root, measured by lowest `origin_time`
    (if available) or otherwise lowest `id`.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_mark_roots(phylogeny_df, mutate=True)
    if len(phylogeny_df) <= 1:
        phylogeny_df["is_oldest_root"] = True
        return phylogeny_df

    phylogeny_df.reset_index(drop=True, inplace=True)
    idxmin: int
    if "origin_time" in phylogeny_df.columns:
        idxmin = (
            phylogeny_df.loc[phylogeny_df["is_root"]]
            .sort_values(by=["origin_time", "id"])
            .index[0]
        )
    else:
        idxmin = phylogeny_df.loc[phylogeny_df["is_root"], "id"].idxmin()

    phylogeny_df["is_oldest_root"] = False
    phylogeny_df.at[idxmin, "is_oldest_root"] = True

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Mark the oldest root row with an `is_oldest_root` column.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_oldest_root",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_mark_oldest_root", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_mark_oldest_root,
            ),
        )
