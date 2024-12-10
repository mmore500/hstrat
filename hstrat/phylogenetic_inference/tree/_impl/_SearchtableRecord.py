import dataclasses
import typing


@dataclasses.dataclass(slots=True)
class SearchtableRecord:
    rank: int
    taxon_id: int
    taxon_label: str
    search_first_child_id: int = 0
    search_next_sibling_id: int = 0
    search_ancestor_id: int = 0
    ancestor_id: int = 0  # represents parent in the build tree
    differentia: typing.Optional[int] = None
