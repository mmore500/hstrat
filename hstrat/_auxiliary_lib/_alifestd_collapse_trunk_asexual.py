import argparse
import functools
import logging
import os

from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import joinem
import numpy as np
import pandas as pd

from ._add_bool_arg import add_bool_arg
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_oldest_root import alifestd_mark_oldest_root
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
def alifestd_collapse_trunk_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Collapse entries masked by `is_trunk` column, keeping only the oldest
    root.

    Masked entries must be contiguous, meaning that no non-trunk entry can
    be an ancestor of a trunk entry.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    See Also
    --------
    alifestd_delete_trunk_asexual
    """
    if "is_trunk" not in phylogeny_df:
        raise ValueError(
            "`is_trunk` column not provided, trunk is unspecified"
        )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["ancestor_is_trunk"] = phylogeny_df.loc[
        phylogeny_df["ancestor_id"], "is_trunk"
    ].to_numpy()

    if np.any(phylogeny_df["is_trunk"] & ~phylogeny_df["ancestor_is_trunk"]):
        raise ValueError("specified trunk is non-contiguous")

    if phylogeny_df["is_trunk"].sum() <= 1:
        return phylogeny_df

    trunk_df = phylogeny_df.loc[phylogeny_df["is_trunk"]].copy()
    trunk_df = alifestd_mark_oldest_root(trunk_df, mutate=True)
    collapsed_root_id = trunk_df.loc[trunk_df["is_oldest_root"].idxmax(), "id"]
    del trunk_df

    if "ancestor_id" in phylogeny_df:
        phylogeny_df.loc[
            phylogeny_df["ancestor_is_trunk"], "ancestor_id"
        ] = collapsed_root_id

    if "ancestor_list" in phylogeny_df:
        phylogeny_df.loc[
            phylogeny_df["ancestor_is_trunk"], "ancestor_list"
        ] = f"[{collapsed_root_id}]"
        phylogeny_df.loc[collapsed_root_id, "ancestor_list"] = "[none]"

    res = phylogeny_df.loc[
        ~phylogeny_df["is_trunk"] | (phylogeny_df["id"] == collapsed_root_id)
    ].reset_index(drop=True)

    assert res["is_trunk"].sum() <= 1
    return res


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Collapse entries masked by `is_trunk` column, keeping only the oldest root.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_collapse_trunk_asexual",
        dfcli_version=get_hstrat_version(),
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
        "hstrat._auxiliary_lib._alifestd_collapse_trunk_asexual", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_collapse_trunk_asexual,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            ),
        )
