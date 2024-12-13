import dataclasses
import typing


@dataclasses.dataclass(slots=True)
class SearchtableRecord:
    """Implementation detail for Searchtable."""

    rank: int
    taxon_id: int  # corresponds to alife standard `id`
    taxon_label: str

    ancestor_id: int = 0  # represents parent in the build tree
    differentia: typing.Optional[int] = None
    search_first_child_id: int = 0  # helper for downward traversal
    search_next_sibling_id: int = 0  # helper for downward traversal
    search_ancestor_id: int = 0  # parent in the search tree
