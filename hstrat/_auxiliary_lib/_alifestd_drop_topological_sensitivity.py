import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd

from ._alifestd_check_topological_sensitivity import (
    alifestd_check_topological_sensitivity,
)
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_drop_topological_sensitivity(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    insert: bool = True,
    delete: bool = True,
    update: bool = True,
) -> pd.DataFrame:
    """Drop columns from `phylogeny_df` that may be invalidated by
    topological operations such as collapsing unifurcations.

    Parameters
    ----------
    phylogeny_df : pandas.DataFrame
        The phylogeny as a dataframe in alife standard format.
    mutate : bool, default False
        Are side effects on the input argument allowed?
    insert : bool, default True
        Drop columns sensitive to node insertion.
    delete : bool, default True
        Drop columns sensitive to node deletion.
    update : bool, default True
        Drop columns sensitive to ancestor relationship updates.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    See Also
    --------
    alifestd_drop_topological_sensitivity_polars :
        Polars-based implementation.
    """
    to_drop = alifestd_check_topological_sensitivity(
        phylogeny_df, insert=insert, delete=delete, update=update,
    )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df.drop(columns=to_drop, inplace=True)
    return phylogeny_df


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
hstrat._auxiliary_lib._alifestd_drop_topological_sensitivity_polars :
    Entrypoint for high-performance Polars-based implementation.
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
            "._alifestd_drop_topological_sensitivity"
        ),
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib"
        "._alifestd_drop_topological_sensitivity",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_drop_topological_sensitivity,
            ),
        )
