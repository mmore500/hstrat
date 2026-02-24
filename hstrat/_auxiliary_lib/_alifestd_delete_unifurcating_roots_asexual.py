import argparse
import functools
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd

from ._add_bool_arg import add_bool_arg
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_asexual import alifestd_is_asexual
from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_mark_num_children_asexual import (
    alifestd_mark_num_children_asexual,
)
from ._alifestd_mark_roots import alifestd_mark_roots
from ._alifestd_topological_sensitivity_warned import (
    alifestd_topological_sensitivity_warned,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


@alifestd_topological_sensitivity_warned(
    insert=False,
    delete=True,
    update=True,
)
def alifestd_delete_unifurcating_roots_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    root_ancestor_token: str = "none",
) -> pd.DataFrame:
    """Pare record to bypass root nodes with only one descendant.

    Dataframe reindexing (e.g., df.index) may be applied.

    See also `alifestd_collapse_unifurcations`.

    The option `root_ancestor_token` will be sandwiched in brackets to create
    the ancestor list entry for genesis organisms. For example, the token
    "None" will yield the entry "[None]" and the token "" will yield the entry
    "[]". Default "none".

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly asexual")

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if "num_children" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_num_children_asexual(
            phylogeny_df, mutate=True
        )
    if "is_root" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_roots(phylogeny_df, mutate=True)

    phylogeny_df["is_unifurcating_root"] = (
        phylogeny_df["num_children"] == 1
    ) & phylogeny_df["is_root"]

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.set_index("id", drop=False, inplace=True)

    phylogeny_df["ancestor_is_unifurcating_root"] = phylogeny_df.loc[
        phylogeny_df["ancestor_id"].values, "is_unifurcating_root"
    ].values

    phylogeny_df.loc[
        phylogeny_df["ancestor_is_unifurcating_root"].values,
        "ancestor_id",
    ] = phylogeny_df.loc[
        phylogeny_df["ancestor_is_unifurcating_root"],
        "id",
    ].values

    phylogeny_df = phylogeny_df[~phylogeny_df["is_unifurcating_root"]].copy()

    if "ancestor_list" in phylogeny_df:
        phylogeny_df.loc[:, "ancestor_list"] = alifestd_make_ancestor_list_col(
            phylogeny_df["id"],
            phylogeny_df["ancestor_id"],
            root_ancestor_token=root_ancestor_token,
        )

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Pare record to bypass root nodes with only one descendant.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_delete_unifurcating_roots_asexual",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "--root-ancestor-token",
        type=str,
        default="none",
        help='token for root ancestor entries (default: "none")',
    )
    add_bool_arg(
        parser,
        "ignore-topological-sensitivity",
        default=False,
        help="suppress topological sensitivity warning (default: False)",
    )
    add_bool_arg(
        parser,
        "drop-topological-sensitivity",
        default=False,
        help="drop topology-sensitive columns from output (default: False)",
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_delete_unifurcating_roots_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_delete_unifurcating_roots_asexual,
                    root_ancestor_token=args.root_ancestor_token,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            ),
        )
