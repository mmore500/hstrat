import argparse
import functools
import logging
import os
import sys
import typing

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import pandas as pd

from ._alifestd_find_leaf_ids import alifestd_find_leaf_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_prune_extinct_lineages_asexual import (
    alifestd_prune_extinct_lineages_asexual,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration
from ._with_rng_state_context import with_rng_state_context


def _alifestd_downsample_tips_asexual_impl(
    phylogeny_df: pd.DataFrame,
    n_downsample: int,
) -> pd.DataFrame:
    """Implementation detail for alifestd_downsample_tips_asexual."""
    tips = alifestd_find_leaf_ids(phylogeny_df)
    kept = np.random.choice(tips, min(n_downsample, len(tips)), replace=False)
    if alifestd_has_contiguous_ids(phylogeny_df):
        extant = np.zeros(len(phylogeny_df), dtype=bool)
        extant[kept] = True
        phylogeny_df["extant"] = extant
    else:
        phylogeny_df["extant"] = phylogeny_df["id"].isin(kept)

    return alifestd_prune_extinct_lineages_asexual(
        phylogeny_df, mutate=True
    ).drop(columns=["extant"])


def alifestd_downsample_tips_asexual(
    phylogeny_df: pd.DataFrame,
    n_downsample: int,
    mutate: bool = False,
    seed: typing.Optional[int] = None,
) -> pd.DataFrame:
    """Create a subsample phylogeny containing `num_tips` tips. If `num_tips`
    is greater than the number of tips in the phylogeny, the whole phylogeny is
    returned.

    Only supports asexual phylogenies.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    if "ancestor_id" not in phylogeny_df.columns:
        raise ValueError(
            "alifestd_downsample_tips_asexual only supports "
            "asexual phylogenies.",
        )

    if phylogeny_df.empty:
        return phylogeny_df

    impl = (
        with_rng_state_context(seed)(_alifestd_downsample_tips_asexual_impl)
        if seed is not None
        else _alifestd_downsample_tips_asexual_impl
    )

    return impl(phylogeny_df, n_downsample)


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Create a subsample phylogeny containing `num_tips` tips.

If `num_tips` is greater than the number of tips in the phylogeny, the whole phylogeny is returned.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_downsample_tips_asexual",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "-n",
        default=sys.maxsize,
        type=int,
        help="Number of tips to subsample.",
    )
    parser.add_argument(
        "--seed",
        default=None,
        dest="seed",
        help="Integer seed for deterministic behavior.",
        type=int,
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_downsample_tips_asexual", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_downsample_tips_asexual,
                    n_downsample=args.n,
                    seed=args.seed,
                ),
            ),
            overridden_arguments="ignore",  # seed is overridden
        )
