import anytree

from ...._auxiliary_lib import render_to_base64url


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

    @property
    def taxon(self: "TrieLeafNode") -> str:
        """Return the taxon label for this leaf node."""
        return self.taxon_label

    @property
    def rank(self: "TrieLeafNode") -> int:
        """Return the origin time for this leaf node."""
        return self.parent.rank

    def __repr__(self: "TrieLeafNode") -> str:
        """Return a string representation of this leaf node."""
        return f"""{self.taxon_label} @ {
            render_to_base64url(id(self) % 8192)
        }"""
