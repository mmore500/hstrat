import typing

from astropy.utils.decorators import deprecated_renamed_argument
import dendropy as dp
import opytional as opyt

from ..._auxiliary_lib import (
    HereditaryStratigraphicInstrument,
    cast_int_lossless,
)
from ._descend_template_phylogeny import descend_template_phylogeny


@deprecated_renamed_argument("seed_column", "seed_instrument", since="1.20.0")
def descend_template_phylogeny_dendropy(
    tree: dp.Tree,
    seed_instrument: HereditaryStratigraphicInstrument,
    extant_nodes: typing.Optional[typing.Iterable[dp.Node]] = None,
    progress_wrap: typing.Callable = lambda x: x,
) -> typing.List[HereditaryStratigraphicInstrument]:
    """Generate a population of hereditary stratigraphic instruments that could
    have resulted from the template phylogeny.

    Parameters
    ----------
    tree : dendropy.Tree
        Phylogeny record as a dendropy Tree.
    seed_instrument : HereditaryStratigraphicInstrument
        Hereditary stratigraphic instrument to seed at root node of phylogeny.

        Returned hereditary stratigraphic instrument population will be
        generated as if repeatedly calling `CloneDescendant()` on
        `seed_instrument`. As such, specifies configuration (i.e., differentia
        bit width and stratum retention policy) for returned instruments. May
        already have strata deposited, which will be incorporated into generated
        extant population.
    extant_nodes : optional list of dendropy.Node
        Which organisms should hereditary stratigraphic instruments be created
        for?

        Designates content and order of returned list of hereditary
        stratigraphic instrument.

        If None, hereditary stratigraphic instruments will be created for all
        phylogenetic leaves (organisms without offspring) in order of
        appearance in `tree.leaf_node_iter()`.
    progress_wrap : Callable, optional
        Wrapper applied around generation iterator and row generator for final
        phylogeny compilation process.

        Pass tqdm or equivalent to display progress bars.

    Returns
    -------
    list of HereditaryStratigraphicInstrument
        Population of hereditary stratigraphic instruments for extant lineage
        members (i.e., phylogeny leaf nodes).

        Instruments ordered in order of appearance of corresponding extant
        organism id.
    """

    return descend_template_phylogeny(
        ascending_lineage_iterables=(
            extant_node.ancestor_iter(
                inclusive=True,
            )
            for extant_node in opyt.or_value(
                extant_nodes, tree.leaf_node_iter()
            )
        ),
        descending_tree_iterable=tree.levelorder_node_iter(),
        get_parent=lambda node: node.parent_node,
        get_stem_length=lambda node: cast_int_lossless(
            node.edge_length, action="warn", context="edge length"
        ),
        seed_instrument=seed_instrument,
        demark=id,
        progress_wrap=progress_wrap,
    )
