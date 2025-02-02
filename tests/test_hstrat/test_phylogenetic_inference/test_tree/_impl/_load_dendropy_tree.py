import alifedata_phyloinformatics_convert as apc
import dendropy as dp
import pandas as pd

from hstrat._auxiliary_lib import alifestd_add_inner_leaves


def load_dendropy_tree(path: str, add_inner_leaves: bool = False) -> dp.Tree:
    if path.endswith(".csv"):
        alifestd_df = pd.read_csv(path)
        if add_inner_leaves:
            alifestd_df = alifestd_add_inner_leaves(alifestd_df)
        return apc.alife_dataframe_to_dendropy_tree(
            alifestd_df,
            setup_edge_lengths=True,
        )
    elif path.endswith(".newick"):
        return dp.Tree.get(path=path, schema="newick")
