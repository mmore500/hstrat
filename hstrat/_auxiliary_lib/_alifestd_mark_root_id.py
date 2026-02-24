import argparse
import logging
import os
import typing

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_mark_root_id(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    selector: typing.Callable = min,
) -> pd.DataFrame:
    """Add column `root_id`, containing the `id` of entries' ultimate ancestor.

    For sexual data, the field `root_id` is chosen according to the selection
    of callable `selector` over parents' `root_id` values. Note that subsets
    within a connected component may be marked with different `root_id` values.
    To create a component id that is consistent within connected components,
    a backward pass could be performed that updates ancestors' values if they
    are greater than that of each descendant.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["root_id"] = phylogeny_df["id"]
    if "ancestor_id" in phylogeny_df.columns:  # asexual
        root_id_col = phylogeny_df["root_id"]
        ancestor_id_col = phylogeny_df["ancestor_id"]
        for index in phylogeny_df.index:
            ancestor_id = ancestor_id_col.at[index]
            root_id_col.at[index] = root_id_col.at[ancestor_id]
    else:  # sexual
        root_id_col = phylogeny_df["root_id"]
        ancestor_list_col = phylogeny_df["ancestor_list"]
        for index in phylogeny_df.index:
            ancestor_list = ancestor_list_col.at[index]
            ancestor_ids = alifestd_parse_ancestor_ids(ancestor_list)
            candidate_roots = [*map(root_id_col.at.__getitem__, ancestor_ids)]
            # "or" covers genesis empty list case
            root_id_col.at[index] = selector(candidate_roots or [index])

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add column `root_id`, containing the `id` of entries' ultimate ancestor.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_root_id",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_mark_root_id", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_mark_root_id,
            ),
        )
