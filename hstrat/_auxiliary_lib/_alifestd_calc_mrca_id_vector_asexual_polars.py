import argparse
import logging
import os
import typing

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import polars as pl

from ._alifestd_calc_mrca_id_vector_asexual import (
    _alifestd_calc_mrca_id_vector_asexual_fast_path,
)
from ._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)
from ._alifestd_is_topologically_sorted_polars import (
    alifestd_is_topologically_sorted_polars,
)
from ._alifestd_mark_node_depth_asexual import (
    _alifestd_calc_node_depth_asexual_contiguous,
)
from ._alifestd_try_add_ancestor_id_col_polars import (
    alifestd_try_add_ancestor_id_col_polars,
)
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_calc_mrca_id_vector_asexual_polars(
    phylogeny_df: pl.DataFrame,
    *,
    target_id: int,
    progress_wrap: typing.Callable = lambda x: x,
) -> np.ndarray:
    """Calculate the Most Recent Common Ancestor (MRCA) taxon id for
    target_id and each other taxon.

    Taxa sharing no common ancestor will have MRCA id -1.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame or polars.LazyFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny in working format (i.e.,
        topologically sorted with contiguous ids and an ancestor_id
        column, or an ancestor_list column from which ancestor_id can
        be derived).
    target_id : int
        The target organism id to compute MRCA against.
    progress_wrap : callable, optional
        Wrapper for progress display (e.g., tqdm).

    Returns
    -------
    numpy.ndarray
        Array of shape (n,) with dtype int64, containing MRCA ids for
        each organism with the target.  Entries are -1 where organisms
        share no common ancestor with the target.

    See Also
    --------
    alifestd_calc_mrca_id_vector_asexual :
        Pandas-based implementation.
    """
    phylogeny_df = alifestd_try_add_ancestor_id_col_polars(phylogeny_df)

    if not alifestd_has_contiguous_ids_polars(phylogeny_df):
        raise NotImplementedError(
            "non-contiguous ids not yet supported",
        )

    if not alifestd_is_topologically_sorted_polars(phylogeny_df):
        raise NotImplementedError(
            "topologically unsorted rows not yet supported",
        )

    ancestor_ids = (
        phylogeny_df.lazy()
        .select("ancestor_id")
        .collect()
        .to_series()
        .to_numpy()
    )

    n = len(ancestor_ids)
    if n == 0:
        raise ValueError(f"{target_id=} out of bounds")
    if target_id >= n:
        raise ValueError(f"{target_id=} out of bounds")

    node_depths = _alifestd_calc_node_depth_asexual_contiguous(
        ancestor_ids,
    )

    return _alifestd_calc_mrca_id_vector_asexual_fast_path(
        ancestor_ids, node_depths, target_id, progress_wrap
    )


_raw_description = f"""\
{os.path.basename(__file__)} | \
(hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Calculate the MRCA taxon id vector for a target taxon vs all other taxa.

Data is assumed to be in alife standard format.

Additional Notes
================
- Requires 'ancestor_id' column (or 'ancestor_list' column from which \
ancestor_id can be derived).

- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.

See Also
========
hstrat._auxiliary_lib._alifestd_calc_mrca_id_vector_asexual :
    CLI entrypoint for Pandas-based implementation.
"""


def _cli_op(phylogeny_df: pl.DataFrame) -> pl.DataFrame:
    """CLI wrapper that computes the MRCA vector for target_id and
    attaches it as a column."""
    target_id = _cli_op._target_id  # set before calling
    mrca_ids = alifestd_calc_mrca_id_vector_asexual_polars(
        phylogeny_df, target_id=target_id
    )
    return phylogeny_df.with_columns(
        mrca_id=pl.Series(mrca_ids),
    )


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--target-id",
        type=int,
        default=0,
        help="Target organism id to compute MRCA against (default: 0).",
    )
    parser = _add_parser_base(
        parser=parser,
        dfcli_module=(
            "hstrat._auxiliary_lib"
            "._alifestd_calc_mrca_id_vector_asexual_polars"
        ),
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    _cli_op._target_id = args.target_id

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib"
            "._alifestd_calc_mrca_id_vector_asexual_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=_cli_op,
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
