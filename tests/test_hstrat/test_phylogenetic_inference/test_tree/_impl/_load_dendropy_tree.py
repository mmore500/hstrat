import alifedata_phyloinformatics_convert as apc
import dendropy as dp
import pandas as pd


def load_dendropy_tree(path: str) -> dp.Tree:
    if path.endswith(".csv"):
        alifestd_df = pd.read_csv(path)
        return apc.alife_dataframe_to_dendropy_tree(
            alifestd_df,
            setup_edge_lengths=True,
        )
    elif path.endswith(".newick"):
        return dp.Tree.get(path=path, schema="newick")
