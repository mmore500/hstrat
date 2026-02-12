import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd

from ._alifestd_find_leaf_ids import alifestd_find_leaf_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_leaves_polars import alifestd_mark_leaves_polars
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_mark_leaves(
    phylogeny_df: pd.DataFrame, mutate: bool = False
) -> pd.DataFrame:
    """What rows are ancestor to no other row?

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    leaf_ids = alifestd_find_leaf_ids(phylogeny_df)
    phylogeny_df["is_leaf"] = False
    phylogeny_df.loc[leaf_ids, "is_leaf"] = True

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Mark rows that are ancestor to no other row with an `is_leaf` column.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_leaves",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    _pandas_fallback = delegate_polars_implementation()(
        alifestd_mark_leaves,
    )

    def _try_polars_op(df):
        try:
            return alifestd_mark_leaves_polars(df)
        except NotImplementedError:
            logging.info("- polars not supported, falling back to pandas")
            return _pandas_fallback(df)

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_mark_leaves", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=_try_polars_op,
        )
