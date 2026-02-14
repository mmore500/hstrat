import argparse
import functools
import logging
import os
import sys

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


def alifestd_prune_canopy_asexual(
    phylogeny_df: pd.DataFrame,
    num_tips: int,
    mutate: bool = False,
) -> pd.DataFrame:
    """Retain the `num_tips` leaves with the highest ids and prune extinct
    lineages.

    If `num_tips` is greater than or equal to the number of leaves in the
    phylogeny, the whole phylogeny is returned.

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

    Returns
    -------
    pandas.DataFrame
        The pruned phylogeny in alife standard format.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    if "ancestor_id" not in phylogeny_df.columns:
        raise ValueError(
            "alifestd_prune_canopy_asexual only supports "
            "asexual phylogenies.",
        )

    if phylogeny_df.empty:
        return phylogeny_df

    tips = alifestd_find_leaf_ids(phylogeny_df)
    tips_sorted = np.sort(tips)
    kept = tips_sorted[-num_tips:]  # highest ids
    if alifestd_has_contiguous_ids(phylogeny_df):
        extant = np.zeros(len(phylogeny_df), dtype=bool)
        extant[kept] = True
        phylogeny_df["extant"] = extant
    else:
        phylogeny_df["extant"] = phylogeny_df["id"].isin(kept)

    return alifestd_prune_extinct_lineages_asexual(
        phylogeny_df, mutate=True
    ).drop(columns=["extant"])


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Retain the `-n` leaves with the highest ids and prune extinct lineages.

If `-n` is greater than or equal to the number of leaves in the phylogeny, the whole phylogeny is returned.

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
hstrat._auxiliary_lib._alifestd_prune_canopy_polars :
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
        dfcli_module="hstrat._auxiliary_lib._alifestd_prune_canopy_asexual",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "-n",
        default=sys.maxsize,
        type=int,
        help="Number of tips to retain.",
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_prune_canopy_asexual", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_prune_canopy_asexual,
                    num_tips=args.n,
                ),
            ),
        )
