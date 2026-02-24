import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_mark_right_child_asexual import (
    alifestd_mark_right_child_asexual,
)
from ._alifestd_mark_roots import alifestd_mark_roots
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_mark_is_right_child_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `is_right_child`, containing for each node whether it is the
    larger-id child.

    Root nodes will be marked False. Tree must be strictly bifurcating.

    Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly bifurcating")

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if "right_child_id" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_right_child_asexual(
            phylogeny_df, mutate=True
        )

    if "is_root" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_roots(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["is_right_child"] = (
        phylogeny_df.loc[phylogeny_df["ancestor_id"], "right_child_id"].values
        == phylogeny_df["id"].values
    ) & ~phylogeny_df["is_root"].values

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add column `is_right_child`, containing for each node whether it is the larger-id child.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_is_right_child_asexual",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_mark_is_right_child_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_mark_is_right_child_asexual,
            ),
        )
