import argparse
import functools
import logging
import os
import sys

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import pandas as pd

from ._add_bool_arg import add_bool_arg
from ._alifestd_calc_mrca_id_vector_asexual import (
    alifestd_calc_mrca_id_vector_asexual,
)
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_leaves import alifestd_mark_leaves
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
def alifestd_downsample_tips_lineage_asexual(
    phylogeny_df: pd.DataFrame,
    num_tips: int,
    mutate: bool = False,
    *,
    criterion_relatedness: str = "origin_time",
    criterion_target: str = "origin_time",
) -> pd.DataFrame:
    """Retain the `num_tips` leaves closest to the lineage of a target
    leaf.

    A target leaf is chosen as the leaf with the largest
    `criterion_target` value. For each leaf, the MRCA (Most Recent Common
    Ancestor) with the target is computed and the "off-lineage delta" is
    calculated as the leaf's `criterion_relatedness` value minus its MRCA's
    `criterion_relatedness` value. The `num_tips` leaves with the smallest
    off-lineage deltas are retained.

    If `num_tips` is greater than or equal to the number of leaves in the
    phylogeny, the whole phylogeny is returned. Ties are broken
    arbitrarily.

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
    criterion_relatedness : str, default "origin_time"
        Column name used to compute off-lineage delta for each leaf. The
        delta is the leaf's value minus its MRCA's value with respect to
        the target leaf.
    criterion_target : str, default "origin_time"
        Column name used to select the target leaf. The leaf with the
        largest value in this column is chosen as the target.

    Raises
    ------
    ValueError
        If `criterion_relatedness` or `criterion_target` is not a column
        in `phylogeny_df`.

    Returns
    -------
    pandas.DataFrame
        The pruned phylogeny in alife standard format.
    """
    for criterion in criterion_relatedness, criterion_target:
        if criterion not in phylogeny_df.columns:
            raise ValueError(
                f"criterion column {criterion!r} not found in phylogeny_df",
            )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    if "ancestor_id" not in phylogeny_df.columns:
        raise ValueError(
            "alifestd_downsample_tips_lineage_asexual only supports "
            "asexual phylogenies.",
        )

    if "is_leaf" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_leaves(phylogeny_df)

    if phylogeny_df.empty:
        return phylogeny_df

    leaf_df = phylogeny_df.loc[phylogeny_df["is_leaf"]]

    target_id = (
        leaf_df.loc[
            leaf_df[criterion_target] == leaf_df[criterion_target].max(),
            "id",
        ]
        .sample(n=1)
        .iloc[0]
    )

    mrca_vector = alifestd_calc_mrca_id_vector_asexual(
        phylogeny_df, target_id=target_id
    )

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    # Taxa with no common ancestor (different tree) get -1 from MRCA calc;
    # replace with the taxon's own id so the lookup doesn't fail, then
    # assign inf delta so they are never selected by nsmallest.
    no_mrca_mask = mrca_vector == -1
    safe_mrca = np.where(
        no_mrca_mask, phylogeny_df["id"].to_numpy(), mrca_vector
    )

    delta = (
        phylogeny_df[criterion_relatedness].to_numpy()
        - phylogeny_df.loc[safe_mrca, criterion_relatedness].to_numpy()
    ).astype(float)
    delta[no_mrca_mask] = np.inf

    phylogeny_df[
        "_alifestd_downsample_tips_lineage_aseuxal_off_lineage_delta"
    ] = delta
    phylogeny_df["extant"] = False
    phylogeny_df.loc[
        phylogeny_df.loc[phylogeny_df["is_leaf"]]
        .nsmallest(
            num_tips,
            "_alifestd_downsample_tips_lineage_aseuxal_off_lineage_delta",
        )
        .index,
        "extant",
    ] = True

    phylogeny_df.drop(
        columns=[
            "_alifestd_downsample_tips_lineage_aseuxal_off_lineage_delta",
        ],
        inplace=True,
    )

    return alifestd_prune_extinct_lineages_asexual(
        phylogeny_df, mutate=True
    ).drop(columns=["extant"])


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Retain the `-n` leaves closest to the lineage of a target leaf.

The target leaf is chosen as the leaf with the largest `--criterion-target` value. For each leaf, the off-lineage delta is computed as the leaf's `--criterion-relatedness` value minus its MRCA's `--criterion-relatedness` value with respect to the target. The `-n` leaves with the smallest deltas are retained.

If `-n` is greater than or equal to the number of leaves in the phylogeny, the whole phylogeny is returned. Ties are broken arbitrarily.

Data is assumed to be in alife standard format.
Only supports asexual phylogenies.

Additional Notes
================
- Requires 'ancestor_id' column to be present in input DataFrame.
Otherwise, no action is taken.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_asexual",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "-n",
        default=sys.maxsize,
        type=int,
        help="Number of tips to retain.",
    )
    parser.add_argument(
        "--criterion-relatedness",
        default="origin_time",
        type=str,
        help="Column used to compute off-lineage delta (default: origin_time).",
    )
    parser.add_argument(
        "--criterion-target",
        default="origin_time",
        type=str,
        help="Column used to select the target leaf (default: origin_time).",
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
        "hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_downsample_tips_lineage_asexual,
                    num_tips=args.n,
                    criterion_relatedness=args.criterion_relatedness,
                    criterion_target=args.criterion_target,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            ),
        )
