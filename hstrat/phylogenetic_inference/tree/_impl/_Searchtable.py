import dataclasses
import itertools as it
import typing

import opytional as opyt

from ._SearchtableRecord import SearchtableRecord


class Searchtable:

    _records: typing.List[SearchtableRecord]

    def __init__(self: "Searchtable") -> None:
        self._records = [
            SearchtableRecord(rank=0, taxon_id=0, taxon_label="_root"),
        ]

    def get_differentia_of(self: "Searchtable", taxon_id: int) -> int:
        return self._records[taxon_id].differentia

    def get_rank_of(self: "Searchtable", taxon_id: int) -> int:
        return self._records[taxon_id].rank

    def get_records(self: "Searchtable") -> typing.List[dict]:
        return [*map(dataclasses.asdict, self._records)]

    def has_search_parent(self: "Searchtable", taxon_id: int) -> bool:
        return self._records[taxon_id].search_ancestor_id != taxon_id

    def iter_children_of(
        self: "Searchtable", taxon_id: int
    ) -> typing.Iterable[int]:
        prev = taxon_id
        cur = self._records[taxon_id].search_first_child_id
        while cur != prev:
            yield cur
            prev = cur
            cur = self._records[cur].search_next_sibling_id

    def iter_inner_children_of(
        self: "Searchtable",
        taxon_id: int,
    ) -> typing.Iterable[int]:
        for child in self.iter_children_of(taxon_id):
            if self._records[taxon_id].search_first_child_id != taxon_id:
                yield child

    def attach_search_parent(
        self: "Searchtable", *, taxon_id: int, parent_id: int
    ) -> None:
        if self._records[taxon_id].search_ancestor_id == parent_id:
            return

        self._records[taxon_id].search_ancestor_id = parent_id

        ancestor_first_child = self._records[parent_id].search_first_child_id
        is_first_child_ = ancestor_first_child == parent_id
        new_next_sibling = (
            taxon_id if is_first_child_ else ancestor_first_child
        )
        self._records[taxon_id].search_next_sibling_id = new_next_sibling
        self._records[parent_id].search_first_child_id = taxon_id

    def detach_search_parent(self: "Searchtable", taxon_id: int) -> None:
        ancestor_id = self._records[taxon_id].search_ancestor_id
        assert self.has_search_parent(taxon_id)

        is_first_child_ = (
            self._records[ancestor_id].search_first_child_id == taxon_id
        )
        next_sibling = self._records[taxon_id].search_next_sibling_id
        is_last_child = next_sibling == taxon_id

        if is_first_child_:
            new_first_child = ancestor_id if is_last_child else next_sibling
            self._records[ancestor_id].search_first_child_id = new_first_child
        else:
            for child1, child2 in it.pairwise(
                self.iter_children_of(ancestor_id),
            ):
                if child2 == taxon_id:
                    new_next_sib = child1 if is_last_child else next_sibling
                    self._records[child1].search_next_sibling_id = new_next_sib
                    break
            else:
                assert False

        self._records[taxon_id].search_ancestor_id = taxon_id
        self._records[taxon_id].search_next_sibling_id = taxon_id

    def create_offspring(
        self: "Searchtable",
        *,
        parent_id: int,
        differentia: int,
        rank: int,
        taxon_label: typing.Optional[str] = None,
    ) -> int:

        taxon_id = len(self._records)
        record = SearchtableRecord(
            ancestor_id=parent_id,
            differentia=differentia,
            rank=rank,
            taxon_id=taxon_id,
            taxon_label=opyt.or_value(taxon_label, f"{len(self._records)}"),
            search_ancestor_id=taxon_id,  # will be set in attach_search_parent
            search_first_child_id=taxon_id,
            search_next_sibling_id=taxon_id,
        )
        self._records.append(record)

        assert not self.has_search_parent(taxon_id)
        self.attach_search_parent(taxon_id=taxon_id, parent_id=parent_id)

        return taxon_id
