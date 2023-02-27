import anytree

from ...._auxiliary_lib import render_to_base64url


class TrieLeafNode(anytree.NodeMixin):

    taxon_label: str

    def __init__(
        self: "TrieLeafNode",
        parent: "TrieInnerNode",
        taxon_label: str,
    ) -> None:
        self.parent = parent
        self.taxon_label = taxon_label

    @property
    def name(self: "TrieLeafNode") -> str:
        return self.taxon_label

    @property
    def taxon(self: "TrieLeafNode") -> str:
        return self.name

    @property
    def origin_time(self: "TrieLeafNode") -> int:
        return self.parent.origin_time

    def __repr__(self: "TrieLeafNode") -> str:
        return f"""{self.taxon_label} @ {
            render_to_base64url(id(self) % 8192)
        }"""
