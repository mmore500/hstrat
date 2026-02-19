import pandas as pd

from ._alifestd_add_inner_knuckles_asexual import (
    alifestd_add_inner_knuckles_asexual,
)
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_mark_node_depth_asexual import alifestd_mark_node_depth_asexual
from ._alifestd_topological_sensitivity_warned import (
    alifestd_topological_sensitivity_warned,
)


@alifestd_topological_sensitivity_warned(
    insert=True,
    delete=False,
    update=True,
)
def alifestd_add_inner_niblings_asexual(
    phylogeny_df: pd.DataFrame, mutate: bool = False
) -> pd.DataFrame:
    """For all inner nodes, add a subtending unifurcation, adding a "nibling"
    leaf as the child of the knuckle.

    Here, "nibling" refers to a leaf that is a neice/nephew of the inner node.
    If not topologically sorted, a topological sort will be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_add_inner_knuckles_asexual(
        phylogeny_df, mutate=True
    )

    phylogeny_df = alifestd_mark_node_depth_asexual(phylogeny_df, mutate=True)

    phylogeny_df = alifestd_mark_leaves(phylogeny_df, mutate=True)

    nibling_mask = (phylogeny_df["node_depth"] & 1).astype(bool) & (
        ~phylogeny_df["is_leaf"]
    )

    nibling_df = phylogeny_df[nibling_mask].copy()

    id_delta = phylogeny_df["id"].max() + 1
    nibling_df["id"] += id_delta
    nibling_df["is_leaf"] = True

    if nibling_df["id"].min() <= phylogeny_df["id"].max():
        print(nibling_df["id"].min(), phylogeny_df["id"].max())
        raise ValueError("overflow in new id assigment")

    return pd.concat([phylogeny_df, nibling_df], ignore_index=True)
