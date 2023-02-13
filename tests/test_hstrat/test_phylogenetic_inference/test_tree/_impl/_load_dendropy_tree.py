import dendropy as dp
import pandas as pd

from ._AuxTree import AuxTree


def load_dendropy_tree(path: str) -> dp.Tree:
    if path.endswith(".csv"):
        alifestd_df = pd.read_csv(path)
        return AuxTree(alifestd_df).dendropy
    elif path.endswith(".newick"):
        return dp.Tree.get(path=path, schema="newick")
