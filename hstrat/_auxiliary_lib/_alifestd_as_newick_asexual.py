from collections import defaultdict
import logging
import typing

import more_itertools as mit
import numpy as np
import opytional as opyt
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_origin_time_delta_asexual import (
    alifestd_mark_origin_time_delta_asexual,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._alifestd_unfurl_traversal_postorder_asexual import (
    alifestd_unfurl_traversal_postorder_asexual,
)

_UNSAFE_SYMBOLS = (";", "(", ")", ",", "[", "]", ":", "'")


def _format_newick_repr(
    label: str,
    children_reprs: typing.List[str],
    origin_time_delta: float,
) -> str:
    # adapted from https://github.com/niemasd/TreeSwift/blob/63b8979fb5e616ba89079d44e594682683c1365e/treeswift/Node.py#L129
    if any(c in label for c in _UNSAFE_SYMBOLS):
        label = f"'{label}'"

    if not np.isnan(origin_time_delta):
        label = f"{label}:{origin_time_delta}"
        if "." in label:
            label = label.rstrip("0").rstrip(".")

    if children_reprs:
        label = f"({','.join(children_reprs)}){label}"

    return label


def alifestd_as_newick_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    label_key: str = "id",
    progress_wrap=lambda x: x,
) -> str:
    """Convert phylogeny dataframe to Newick format."""

    logging.info(
        "creating newick string for alifestd df "
        f"with shape {phylogeny_df.shape}",
    )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    logging.info("adding ancestor id column, if not present")
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    logging.info("setting up `origin_time_delta` column...")
    if "origin_time_delta" in phylogeny_df.columns:
        logging.info("... already present!")
    elif "origin_time" in phylogeny_df.columns:
        logging.info("... calculating from `origin_time`...")
        phylogeny_df = alifestd_mark_origin_time_delta_asexual(
            phylogeny_df, mutate=True
        )
    else:
        logging.info("... marking null")
        phylogeny_df["origin_time_delta"] = np.nan

    logging.info("calculating postorder traversal order...")
    postorder_ids = alifestd_unfurl_traversal_postorder_asexual(phylogeny_df)

    logging.info("preparing labels...")
    phylogeny_df["__hstrat_label"] = opyt.apply_if_or_value(
        label_key, phylogeny_df.__getitem__, ""
    )
    phylogeny_df["__hstrat_label"] = phylogeny_df["__hstrat_label"].astype(str)

    logging.info("creating newick string...")
    child_newick_reprs = defaultdict(list)
    for id_ in progress_wrap(postorder_ids):
        taxon_label = phylogeny_df.at[id_, "__hstrat_label"]
        origin_time_delta = phylogeny_df.at[id_, "origin_time_delta"]

        newick_repr = _format_newick_repr(
            taxon_label, child_newick_reprs.pop(id_, []), origin_time_delta
        )

        ancestor_id = phylogeny_df.at[id_, "ancestor_id"]
        child_newick_reprs[ancestor_id].append(newick_repr)

    logging.info(
        f"finalizing newick string for {len(child_newick_reprs)} trees...",
    )
    result = ";\n".join(map(mit.one, child_newick_reprs.values())) + ";"
    logging.info(f"{len(result)=} {result[:20]=}")
    return result
