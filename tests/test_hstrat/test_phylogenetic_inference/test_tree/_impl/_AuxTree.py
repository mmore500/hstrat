import Bio
import alifedata_phyloinformatics_convert as apc
import dendropy as dp
import pandas as pd


# auxiliary tree class to allow for inter-format conversions
class AuxTree:
    def __init__(self, tree):
        # internal tree representation is an alife-formatted tree
        self._tree = self._alife_dispatcher(tree)

    @property
    def biopython(self):
        return apc.alife_dataframe_to_biopython_tree(
            self._tree, setup_edge_lengths=True
        )

    @property
    def dendropy(self):
        return apc.alife_dataframe_to_dendropy_tree(
            self._tree, setup_edge_lengths=True
        )

    @property
    def alife(self):
        return self._tree

    def _alife_dispatcher(self, tree):
        """
        Convert any supported tree format to ALife format
        """
        if isinstance(tree, dp.Tree):
            # is a Dendropy Tree
            return apc.dendropy_tree_to_alife_dataframe(
                tree
            )  # , {'name': 'taxon_label'})
        if isinstance(tree, pd.DataFrame):
            # is an Alife Dataframe
            # TODO: check these properties exist https://alife-data-standards.github.io/alife-data-standards/phylogeny.html
            return tree
        if isinstance(tree, Bio.Phylo.BaseTree.Tree):
            # is a biopython tree
            return apc.biopython_tree_to_alife_dataframe(
                tree, {"name": "taxon_label"}
            )
