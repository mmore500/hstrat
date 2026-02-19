import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import polars as pl

from ._add_bool_arg import add_bool_arg
from ._alifestd_check_topological_sensitivity_polars import (
    alifestd_check_topological_sensitivity_polars,
)
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_drop_topological_sensitivity_polars(
    phylogeny_df: pl.DataFrame,
    *,
    insert: bool = True,
    delete: bool = True,
    update: bool = True,
) -> pl.DataFrame:
    """Drop columns from `phylogeny_df` that may be invalidated by
    topological operations such as collapsing unifurcations.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame
        The phylogeny as a dataframe in alife standard format.
    insert : bool, default True
        Drop columns sensitive to node insertion.
    delete : bool, default True
        Drop columns sensitive to node deletion.
    update : bool, default True
        Drop columns sensitive to ancestor relationship updates.

    See Also
    --------
    alifestd_drop_topological_sensitivity :
        Pandas-based implementation.
    """
    to_drop = alifestd_check_topological_sensitivity_polars(
        phylogeny_df,
        insert=insert,
        delete=delete,
        update=update,
    )
    return phylogeny_df.drop(to_drop)


_raw_description = f"""\
{os.path.basename(__file__)} | \
(hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Drop columns that may be invalidated by topological operations.

Data is assumed to be in alife standard format.

Additional Notes
================
- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.

See Also
========
hstrat._auxiliary_lib._alifestd_drop_topological_sensitivity :
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
        dfcli_module=(
            "hstrat._auxiliary_lib"
            "._alifestd_drop_topological_sensitivity_polars"
        ),
        dfcli_version=get_hstrat_version(),
    )
    add_bool_arg(
        parser,
        "insert",
        default=True,
        help="drop columns sensitive to node insertion (default: True)",
    )
    add_bool_arg(
        parser,
        "delete",
        default=True,
        help="drop columns sensitive to node deletion (default: True)",
    )
    add_bool_arg(
        parser,
        "update",
        default=True,
        help=(
            "drop columns sensitive to ancestor relationship updates"
            " (default: True)"
        ),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib"
            "._alifestd_drop_topological_sensitivity_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=(
                    lambda df: alifestd_drop_topological_sensitivity_polars(
                        df,
                        insert=args.insert,
                        delete=args.delete,
                        update=args.update,
                    )
                ),
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
