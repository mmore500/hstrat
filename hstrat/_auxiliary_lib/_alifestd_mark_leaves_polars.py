import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import polars as pl

from ._alifestd_mark_num_children_polars import (
    alifestd_mark_num_children_polars,
)
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_mark_leaves_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Add column `is_leaf` marking rows that are ancestor to no other row.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.

    Returns
    -------
    polars.DataFrame
        The phylogeny with an added `is_leaf` boolean column.

    See Also
    --------
    alifestd_mark_leaves :
        Pandas-based implementation.
    """
    if phylogeny_df.lazy().limit(1).collect().is_empty():
        return phylogeny_df.with_columns(
            is_leaf=pl.lit(False),  # sets Boolean dtype, but no values
        )

    if "num_children" not in phylogeny_df.lazy().collect_schema().names():
        phylogeny_df = alifestd_mark_num_children_polars(phylogeny_df)

    return phylogeny_df.with_columns(
        is_leaf=pl.col("num_children") == 0,
    )


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Mark rows that are ancestor to no other row with an `is_leaf` column.

Data is assumed to be in alife standard format.

Additional Notes
================
- Requires 'ancestor_id' column to be present in input DataFrame.
Otherwise, no action is taken.

- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.

See Also
========
hstrat._auxiliary_lib._alifestd_mark_leaves :
    CLI entrypoint for Pandas-based implementation.
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
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_leaves_polars",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()
    logging.info("hstrat version %s", get_hstrat_version())

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_mark_leaves_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=alifestd_mark_leaves_polars,
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
