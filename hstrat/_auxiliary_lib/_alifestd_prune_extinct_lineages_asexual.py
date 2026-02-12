import argparse
import logging
import operator
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._alifestd_unfurl_lineage_asexual import alifestd_unfurl_lineage_asexual
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._jit import jit
from ._log_context_duration import log_context_duration
from ._unfurl_lineage_with_contiguous_ids import (
    unfurl_lineage_with_contiguous_ids,
)


def _create_has_extant_descendant_noncontiguous(
    phylogeny_df: pd.DataFrame,
    extant_mask: np.ndarray,
) -> np.ndarray:
    """Implementation detail for alifestd_prune_extinct_lineages_asexual."""

    phylogeny_df["has_extant_descendant"] = False
    for extant_id in phylogeny_df.loc[extant_mask, "id"]:
        for lineage_id in alifestd_unfurl_lineage_asexual(
            phylogeny_df,
            int(extant_id),
            mutate=True,
        ):
            if phylogeny_df.loc[lineage_id, "has_extant_descendant"]:
                break

            phylogeny_df.loc[lineage_id, "has_extant_descendant"] = True

    return phylogeny_df["has_extant_descendant"]


@jit(nopython=True)
def _create_has_extant_descendant_contiguous(
    ancestor_ids: np.ndarray,
    extant_mask: np.ndarray,
) -> np.ndarray:
    """Implementation detail for alifestd_prune_extinct_lineages_asexual."""

    has_extant_descendant = np.zeros_like(extant_mask)
    for extant_id in np.flatnonzero(extant_mask):
        for lineage_id in unfurl_lineage_with_contiguous_ids(
            ancestor_ids,
            int(extant_id),
        ):
            if has_extant_descendant[lineage_id]:
                break

            has_extant_descendant[lineage_id] = True

    return has_extant_descendant


@jit(nopython=True)
def _create_has_extant_descendant_contiguous_sorted(
    ancestor_ids: np.ndarray,
    extant_mask: np.ndarray,
) -> np.ndarray:
    """Implementation detail for alifestd_prune_extinct_lineages_asexual."""

    has_extant_descendant = extant_mask.copy()
    for id_ in range(len(ancestor_ids) - 1, -1, -1):
        has_extant_descendant[ancestor_ids[id_]] |= has_extant_descendant[id_]

    return has_extant_descendant


def alifestd_prune_extinct_lineages_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Drop taxa without extant descendants.

    An "extant" column, if provided, is used to determine extant taxa.
    Otherwise, taxa with inf or nan "destruction_time" are considered extant.

    Fastest with records in working format. See `alifestd_to_working_format`.

    Parameters
    ----------
    phylogeny_df : pandas.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.
    mutate : bool, default False
        Are side effects on the input argument `phylogeny_df` allowed?

    Raises
    ------
    ValueError
        If `phylogeny_df` has neither "extant" or "destruction_time" columns.

        Without at least one of these columns, which taxa are extant is
        ambiguous.

    Returns
    -------
    pandas.DataFrame
        The rerooted phylogeny in alife standard format.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    extant_mask = None
    if "extant" in phylogeny_df:
        extant_mask = phylogeny_df["extant"]
    elif "destruction_time" in phylogeny_df:
        extant_mask = operator.or_(
            phylogeny_df["destruction_time"].isna(),
            np.isinf(phylogeny_df["destruction_time"]),
        )
    else:
        raise ValueError('Need "extant" or "destruction_time" column.')

    if not alifestd_has_contiguous_ids(phylogeny_df):
        has_extant_descendant = _create_has_extant_descendant_noncontiguous(
            phylogeny_df,
            extant_mask,
        )
    elif not alifestd_is_topologically_sorted(phylogeny_df):
        has_extant_descendant = _create_has_extant_descendant_contiguous(
            phylogeny_df["ancestor_id"].to_numpy(dtype=np.uint64),
            extant_mask.to_numpy(dtype=bool),
        )
    else:
        has_extant_descendant = (
            _create_has_extant_descendant_contiguous_sorted(
                phylogeny_df["ancestor_id"].to_numpy(dtype=np.uint64),
                extant_mask.to_numpy(dtype=bool),
            )
        )

    phylogeny_df = phylogeny_df[has_extant_descendant].reset_index(drop=True)
    phylogeny_df.drop(
        columns="has_extant_descendant", errors="ignore", inplace=True
    )
    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Drop taxa without extant descendants.

An "extant" column, if provided, is used to determine extant taxa.
Otherwise, taxa with inf or nan "destruction_time" are considered extant.

Data is assumed to be in alife standard format.
Only supports asexual phylogenies.

Additional Notes
================
- Requires 'extant' or 'destruction_time' column.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_asexual",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    from ._alifestd_prune_extinct_lineages_asexual_polars import (
        alifestd_prune_extinct_lineages_asexual_polars,
    )

    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation(
                alifestd_prune_extinct_lineages_asexual_polars,
            )(
                alifestd_prune_extinct_lineages_asexual,
            ),
        )
