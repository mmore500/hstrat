import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import polars as pl

from ._alifestd_assign_contiguous_ids import _reassign_ids_asexual
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_assign_contiguous_ids_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Reassign so each organism's id corresponds to its row number.

    Organisms retain the same row location; only id numbers change. Input
    dataframe is not mutated by this operation unless `mutate` True.
    """
    phylogeny_df = phylogeny_df.lazy().collect()  # lazy not yet implemented

    if "ancestor_list" in phylogeny_df.columns:
        raise NotImplementedError

    new_ancestor_ids = _reassign_ids_asexual(
        phylogeny_df["id"].to_numpy(),
        phylogeny_df["ancestor_id"].to_numpy(),
    )

    return (
        phylogeny_df.drop("id")
        .with_row_index("id")
        .with_columns(
            ancestor_id=pl.Series(new_ancestor_ids),
        )
    )


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Reassign so each organism's id corresponds to its row number.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_assign_contiguous_ids_polars",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_assign_contiguous_ids_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=alifestd_assign_contiguous_ids_polars,
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
