import typing

from Bio import Phylo as BioPhylo
import opytional as opyt

from ..._auxiliary_lib import cast_int_lossless
from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._descend_template_phylogeny import descend_template_phylogeny


def descend_template_phylogeny_biopython(
    tree: BioPhylo.BaseTree.Tree,
    seed_column: HereditaryStratigraphicColumn,
    extant_nodes: typing.Optional[
        typing.Iterable[BioPhylo.BaseTree.Clade]
    ] = None,
    progress_wrap: typing.Callable = lambda x: x,
) -> typing.List[HereditaryStratigraphicColumn]:
    """Generate a population of hereditary stratigraphic columns that could
    have resulted from the template phylogeny.

    Parameters
    ----------
    tree : biopython Tree
        Phylogeny record as a biopython Tree.
    seed_column : HereditaryStratigraphicColumn
        Hereditary stratigraphic column to seed at root node of phylogeny.

        Returned hereditary stratigraphic column population will be generated
        as if repeatedly calling `CloneDescendant()` on `seed_column`. As such,
        specifies configuration (i.e., differentia bit width and stratum
        retention policy) for returned columns. May already have strata
        deposited, which will be incorporated into generated extant population.
    extant_nodes : optional list of biopython Clade
        Which organisms should hereditary stratigraphic columns be created for?

        Designates content and order of returned list of hereditary
        stratigraphic column.

        If None, hereditary stratigraphic columns will be created for all
        phylogenetic leaves (organisms without offspring) in order of
        appearance in `tree.leaf_node_iter()`.
    progress_wrap : Callable, default identity function
        Wrapper applied around generation iterator and row generator for final
        phylogeny compilation process.

        Pass tqdm or equivalent to display progress bars.

    Returns
    -------
    list of HereditaryStratigraphicColumn
        Population of hereditary stratigraphic columns for extant lineage
        members (i.e., phylogeny leaf nodes).

        Columns ordered in order of appearance of corresponding extant organism
        id.
    """

    # adapted from https://biopython.org/wiki/Phylo_cookbook
    def all_parents(tree: BioPhylo.BaseTree.Tree) -> typing.Dict:
        parents = {}
        for clade in tree.find_clades(order="level"):
            for child in clade:
                parents[child] = clade
        return parents

    parent_lookup = all_parents(tree)

    return descend_template_phylogeny(
        ascending_lineage_iterables=(
            [extant_node, *tree.trace(extant_node, tree.root)]
            for extant_node in opyt.or_value(
                extant_nodes, tree.get_terminals()
            )
        ),
        descending_tree_iterable=tree.find_clades(),
        get_parent=lambda node: parent_lookup.get(node, None),
        get_stem_length=lambda node: cast_int_lossless(
            opyt.or_value(node.branch_length, 1),
            action="warn",
            context="branch length",
        ),
        seed_column=seed_column,
        demark=id,
        progress_wrap=progress_wrap,
    )
