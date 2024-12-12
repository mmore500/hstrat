import typing

import anytree

from ...._auxiliary_lib import render_to_base64url

if typing.TYPE_CHECKING:  # runtime False, but considered True by type checkers
    from ._TrieInnerNode import TrieInnerNode


class TrieLeafNode(anytree.NodeMixin):
    """A leaf node in a  phylogenetic reconstruction trie.

    Represents an single, specific extant annotation among the population
    subject to phylogenetic inference.

    Parameters
    ----------
    parent : TrieInnerNode
        The parent node of this leaf node.
    taxon_label : str
        The taxon label for this leaf node.

    Attributes
    ----------
    taxon_label : str
        The taxon label for this leaf node.
    taxon : str
        Synonym for taxon_label.
    """

    taxon_label: str

    def __init__(
        self: "TrieLeafNode",
        parent: "TrieInnerNode",
        taxon_label: str,
    ) -> None:
        """Initialize a new TrieLeafNode.

        Parameters
        ----------
        parent : TrieInnerNode
            The parent node of this leaf node.
        taxon_label : str
            The taxon label for this leaf node.
        """
        self.parent = parent
        self.taxon_label = taxon_label

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrieLeafNode):
            return False
        return self.taxon == other.taxon

    @property
    def taxon(self: "TrieLeafNode") -> str:
        """Return the taxon label for this leaf node."""
        return self.taxon_label

    @property
    def rank(self: "TrieLeafNode") -> typing.Optional[int]:
        """Return the origin time for this leaf node."""
        return self.parent.rank

    @property
    def differentia(self: "TrieLeafNode") -> typing.Optional[int]:
        return self.parent.differentia

    def __repr__(self: "TrieLeafNode") -> str:
        """Return a string representation of this leaf node."""
        return f"""{self.taxon_label} @ {
            render_to_base64url(id(self) % 8192)
        }"""

    def __hash__(self: "TrieLeafNode") -> int:
        return hash((self.rank, self.differentia, self.taxon_label))
