import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import polars as pl

from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_try_add_ancestor_id_col_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Add an ancestor_id column to the input DataFrame if the phylogeny is
    asexual and the column does not already exist.
    """

    if "ancestor_id" in phylogeny_df.lazy().collect_schema().names() or (
        phylogeny_df.lazy()
        .select(
            pl.col("ancestor_list").str.contains(",").any(),
        )
        .collect()
        .item()
    ):
        return phylogeny_df

    return phylogeny_df.with_columns(
        ancestor_id=pl.col("ancestor_list")
        .str.extract(r"(\d+)", 1)
        .cast(pl.Int64, strict=False)
        .fill_null(pl.col("id").cast(pl.Int64))
    )


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add an ancestor_id column if the phylogeny is asexual and the column does not already exist.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_try_add_ancestor_id_col_polars",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_try_add_ancestor_id_col_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=alifestd_try_add_ancestor_id_col_polars,
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
