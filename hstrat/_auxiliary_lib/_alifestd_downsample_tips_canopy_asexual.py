import argparse
import functools
import logging
import os
import sys

from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import joinem
import numpy as np
import pandas as pd

from ._add_bool_arg import add_bool_arg
from ._alifestd_find_leaf_ids import alifestd_find_leaf_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_prune_extinct_lineages_asexual import (
    alifestd_prune_extinct_lineages_asexual,
)
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
    update=False,
)
def alifestd_downsample_tips_canopy_asexual(
    phylogeny_df: pd.DataFrame,
    num_tips: int,
    mutate: bool = False,
    criterion: str = "origin_time",
) -> pd.DataFrame:
    """Retain the `num_tips` leaves with the largest `criterion` values and
    prune extinct lineages.

    If `num_tips` is greater than or equal to the number of leaves in the
    phylogeny, the whole phylogeny is returned. Ties are broken arbitrarily.

    Only supports asexual phylogenies.

    Parameters
    ----------
    phylogeny_df : pandas.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.
    num_tips : int
        Number of tips to retain.
    mutate : bool, default False
        Are side effects on the input argument `phylogeny_df` allowed?
    criterion : str, default "origin_time"
        Column name used to rank leaves. The `num_tips` leaves with the
        largest values in this column are retained. Ties are broken
        arbitrarily.

    Raises
    ------
    ValueError
        If `criterion` is not a column in `phylogeny_df`.

    Returns
    -------
    pandas.DataFrame
        The pruned phylogeny in alife standard format.
    """
    if criterion not in phylogeny_df.columns:
        raise ValueError(
            f"criterion column {criterion!r} not found in phylogeny_df",
        )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    if "ancestor_id" not in phylogeny_df.columns:
        raise ValueError(
            "alifestd_downsample_tips_canopy_asexual only supports "
            "asexual phylogenies.",
        )

    if phylogeny_df.empty:
        return phylogeny_df

    if alifestd_has_contiguous_ids(phylogeny_df):
        # With contiguous IDs, id == row index so we can use direct
        # numpy array indexing instead of expensive .isin() calls.
        leaf_positions = alifestd_find_leaf_ids(phylogeny_df)
        leaf_df = phylogeny_df.iloc[leaf_positions]
        kept_ids = leaf_df.nlargest(num_tips, criterion)["id"]
        phylogeny_df["extant"] = np.bincount(
            kept_ids.to_numpy(), minlength=len(phylogeny_df)
        ).astype(bool)
    else:
        tips = alifestd_find_leaf_ids(phylogeny_df)
        leaf_df = phylogeny_df.loc[phylogeny_df["id"].isin(tips)]
        kept_ids = leaf_df.nlargest(num_tips, criterion)["id"]
        phylogeny_df["extant"] = phylogeny_df["id"].isin(kept_ids)

    return alifestd_prune_extinct_lineages_asexual(
        phylogeny_df, mutate=True
    ).drop(columns=["extant"])


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Retain the `-n` leaves with the largest `--criterion` values and prune extinct lineages.

If `-n` is greater than or equal to the number of leaves in the phylogeny, the whole phylogeny is returned. Ties are broken arbitrarily.

Data is assumed to be in alife standard format.
Only supports asexual phylogenies.

Additional Notes
================
- Requires 'ancestor_id' column to be present in input DataFrame.
Otherwise, no action is taken.

- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.

See Also
========
hstrat._auxiliary_lib._alifestd_downsample_tips_canopy_polars :
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
        dfcli_module="hstrat._auxiliary_lib._alifestd_downsample_tips_canopy_asexual",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "-n",
        default=sys.maxsize,
        type=int,
        help="Number of tips to retain.",
    )
    parser.add_argument(
        "--criterion",
        default="origin_time",
        type=str,
        help="Column name used to rank leaves; ties broken arbitrarily (default: origin_time).",
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
        "hstrat._auxiliary_lib._alifestd_downsample_tips_canopy_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_downsample_tips_canopy_asexual,
                    num_tips=args.n,
                    criterion=args.criterion,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            ),
        )
