import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import pandas as pd

from ._alifestd_mark_colless_like_index_mdm_asexual import (
    _alifestd_mark_colless_like_index_asexual_impl,
)
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_mark_colless_like_index_var_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `colless_like_index_var` with Colless-like index
    using sample variance as dissimilarity.

    Computes the Colless-like balance index from Mir, Rossello, and
    Rotger (2018) that supports polytomies. Uses weight function
    f(k) = ln(k + e) and variance dissimilarity.

    For each internal node v with children v_1, ..., v_k:
        bal(v) = var(delta_f(T_v1), ..., delta_f(T_vk))

    where delta_f(T) is the f-size of subtree T, defined as the sum
    of f(deg(u)) over all nodes u in T, and

        var(x_1, ..., x_k) = (1/(k-1)) * sum (x_i - mean(x))^2

    The Colless-like index at a node is the sum of balance values
    across all internal nodes in its subtree.

    Leaf nodes will have Colless-like index 0. The root node contains
    the Colless-like index for the entire tree.

    A topological sort will be applied if `phylogeny_df` is not
    topologically sorted. Dataframe reindexing (e.g., df.index) may
    be applied.

    Input dataframe is not mutated by this operation unless `mutate`
    set True. If mutate set True, operation does not occur in place;
    still use return value to get transformed phylogeny dataframe.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Alife standard DataFrame containing the phylogenetic
        relationships.

    mutate : bool, optional
        If True, modify the input DataFrame in place. Default is
        False.

    Returns
    -------
    pd.DataFrame
        Phylogeny DataFrame with an additional column
        "colless_like_index_var" containing the Colless-like
        imbalance index for the subtree rooted at each node.

    References
    ----------
    Mir, A., Rossello, F., & Rotger, L. (2018). Sound Colless-like
    balance indices for multifurcating trees. PLOS ONE, 13(9),
    e0203401. https://doi.org/10.1371/journal.pone.0203401

    See Also
    --------
    alifestd_mark_colless_like_index_mdm_asexual :
        Colless-like index using MDM dissimilarity.
    alifestd_mark_colless_like_index_sd_asexual :
        Colless-like index using standard deviation dissimilarity.
    alifestd_mark_colless_index_asexual :
        Classic Colless index for strictly bifurcating trees.
    """
    return _alifestd_mark_colless_like_index_asexual_impl(
        phylogeny_df,
        "colless_like_index_var",
        "var",
        mutate=mutate,
    )


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add column `colless_like_index_var` with Colless-like index using sample variance as dissimilarity.

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
        dfcli_module="hstrat._auxiliary_lib._alifestd_mark_colless_like_index_var_asexual",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_mark_colless_like_index_var_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                alifestd_mark_colless_like_index_var_asexual,
            ),
        )
