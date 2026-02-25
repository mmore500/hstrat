import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd

from ._alifestd_find_chronological_inconsistency import (
    alifestd_find_chronological_inconsistency,
)
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_topological_sort import alifestd_topological_sort
from ._begin_prod_logging import begin_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_coerce_chronological_consistency(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """For any taxa with origin time preceding its parent's, set origin time
    to parent's origin time.

    If an inconsistency is detected, the corrected phylogeny will be returned
    sorted in topological order.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if (
        not alifestd_is_topologically_sorted(phylogeny_df)
        and alifestd_find_chronological_inconsistency(phylogeny_df) is not None
    ):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    phylogeny_df = phylogeny_df.set_index("id", drop=False)

    # adapted from https://stackoverflow.com/a/31569794
    origin_time_loc = phylogeny_df.columns.get_loc("origin_time")
    for pos, (_idx, row) in enumerate(phylogeny_df.iterrows()):
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            ancestor_loc = phylogeny_df.index.get_loc(ancestor_id)
            ancestor_time = phylogeny_df.iat[ancestor_loc, origin_time_loc]
            offspring_time = phylogeny_df.iat[pos, origin_time_loc]
            phylogeny_df.iat[pos, origin_time_loc] = max(
                offspring_time, ancestor_time
            )

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

For any taxa with origin time preceding its parent's, set origin time to parent's origin time.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_coerce_chronological_consistency",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    begin_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_coerce_chronological_consistency",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_coerce_chronological_consistency,
            ),
        )
