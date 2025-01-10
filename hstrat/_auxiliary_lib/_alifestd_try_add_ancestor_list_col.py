import argparse
import logging
import os
import warnings

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd
import polars as pl

from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_try_add_ancestor_list_col_polars import (
    alifestd_try_add_ancestor_list_col_polars,
)
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import (
    DataFrame_T,
    delegate_polars_implementation,
)
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


@delegate_polars_implementation(alifestd_try_add_ancestor_list_col_polars)
def alifestd_try_add_ancestor_list_col(
    phylogeny_df: DataFrame_T,
    root_ancestor_token: str = "none",
    mutate: bool = False,
) -> DataFrame_T:
    """Add an ancestor_list column to the input DataFrame if the column does
    not already exist.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    See Also
    --------
    alifestd_make_ancestor_list_col
    """

    assert isinstance(phylogeny_df, pd.DataFrame)
    if "ancestor_id" in phylogeny_df and "ancestor_list" not in phylogeny_df:
        logging.info("ancestor_id column present, adding ancestor_list column")
        if not mutate:
            phylogeny_df = phylogeny_df.copy()
        phylogeny_df["ancestor_list"] = alifestd_make_ancestor_list_col(
            phylogeny_df["id"],
            phylogeny_df["ancestor_id"],
            root_ancestor_token=root_ancestor_token,
        )
    elif "ancestor_list" in phylogeny_df:
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
"""


def _create_parser() -> argparse.ArgumentParser:
    """Create parser for CLI entrypoint."""
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    _add_parser_base(
        parser=parser,
        dfcli_module="hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col",
        dfcli_version=get_hstrat_version(),
    )
    return parser


def _checked_alifestd_add_ancestor_list_col_polars(
    df: pl.DataFrame,
) -> pl.DataFrame:
    """Wrapper for `alifestd_try_add_ancestor_list_col` that checks for
    required columns, preventing silent failure."""

    if "ancestor_id" not in df and "ancestor_list" not in df:
        warnings.warn(
            "Creating 'ancestor_list' column requires 'ancestor_id' column, "
            "but it is not provided.",
        )

    return alifestd_try_add_ancestor_list_col_polars(df)


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=_checked_alifestd_add_ancestor_list_col_polars,
        )
