import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import polars as pl

from ._alifestd_make_ancestor_list_col_polars import (
    alifestd_make_ancestor_list_col_polars,
)
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_try_add_ancestor_list_col_polars(
    phylogeny_df: pl.DataFrame,
    root_ancestor_token: str = "none",
    mutate: bool = False,
) -> pl.DataFrame:
    """Add an ancestor_list column to the input DataFrame if the column does
    not already exist.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    Notes
    -----
    Even allowed by `mutate` flag, no side effects occur on input dataframe
    under Polars implementation. Flag is included for API compatibility with
    Pandas implementation.

    See Also
    --------
    alifestd_try_add_ancestor_list_col :
        Pandas-based implementation.
    """
    is_lazy = isinstance(phylogeny_df, pl.LazyFrame)
    schema_names = phylogeny_df.lazy().collect_schema().names()
    if "ancestor_id" in schema_names and "ancestor_list" not in schema_names:
        logging.info("ancestor_id column present, adding ancestor_list column")
        df_eager = phylogeny_df.lazy().collect()
        result = df_eager.with_columns(
            alifestd_make_ancestor_list_col_polars(
                df_eager["id"],
                df_eager["ancestor_id"],
                root_ancestor_token=root_ancestor_token,
            ).alias("ancestor_list")
        )
        return result.lazy() if is_lazy else result
    elif "ancestor_list" in schema_names:
        logging.info("ancestor_list column already present, skipping addition")
    else:
        logging.info(
            "no ancestor_id column available, skipping ancestor_list addition",
        )

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Create 'ancestor_list' column, if not already present, to comply with Alife standard phylogeny data format.

Additional Notes
================
- Requires 'ancestor_id' column to be present in input DataFrame.
Otherwise, no action is taken.

- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.

See Also
========
hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col :
    CLI entrypoint for Pandas-based implementation.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_parser_base(
        parser=parser,
        dfcli_module="hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col_polars",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col_polars",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=alifestd_try_add_ancestor_list_col_polars,
        )
