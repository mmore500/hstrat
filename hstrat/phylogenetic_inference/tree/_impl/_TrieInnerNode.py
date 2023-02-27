import copy
import functools
import itertools as it
import random
import typing

import anytree
import opytional as opyt

from ...._auxiliary_lib import CopyableSeriesItemsIter, render_to_base64url
from ._TrieLeafNode import TrieLeafNode


class TrieInnerNode(anytree.NodeMixin):

    _rank: int
    _differentia: int
    _tiebreaker: int

    def __init__(
        self: "TrieInnerNode",
        rank: typing.Optional[int] = None,
        differentia: typing.Optional[int] = None,
        parent: typing.Optional["TrieInnerNode"] = None,
    ) -> None:
        self.parent = parent
        self._rank = rank
        self._differentia = differentia
        assert (self._rank is None) == (self._differentia is None)
        self._tiebreaker = random.getrandbits(128)  # uuid standard 128 bits

    def Matches(
        self: "TrieInnerNode",
        rank: int,
        differentia: int,
    ) -> bool:
        return self._rank == rank and self._differentia == differentia

    def GetDescendants(
        self: "TrieInnerNode",
        rank: int,
        differentia: int,
    ) -> typing.Iterator["TrieInnerNode"]:
        assert rank is not None
        assert differentia is not None
        assert (self._differentia is None) == (self._rank is None)
        # handle root case
        if self._rank is None:
            for child in self.inner_children:
                yield from child.GetDescendants(rank, differentia)
        elif rank == self._rank and differentia == self._differentia:
            yield self
        elif rank > self._rank:
            for child in self.inner_children:
                yield from child.GetDescendants(rank, differentia)

    def GetDeepestAlignment(
        self: "TrieInnerNode",
        rank_differentia_iter: CopyableSeriesItemsIter,
    ) -> typing.Optional["TrieInnerNode"]:
        self._cached_rditer = copy.copy(rank_differentia_iter)
        try:
            next_rank, next_differentia = next(rank_differentia_iter)
        except StopIteration:
            return None
        candidates = self.GetDescendants(next_rank, next_differentia)
        return max(
            (
                opyt.or_value(
                    candidate.GetDeepestAlignment(
                        copy.copy(rank_differentia_iter),
                    ),
                    candidate,
                )
                for candidate in candidates
            ),
            default=None,
            key=lambda x: (x._rank, x._tiebreaker)
        )

    def InsertTaxon(
        self: "TrieInnerNode",
        taxon_label: str,
        rank_differentia_iter: CopyableSeriesItemsIter,
    ) -> None:
        try:
            next_rank, next_differentia = next(rank_differentia_iter)
            assert next_rank is not None
            assert next_differentia is not None
            for child in self.inner_children:
                if child.Matches(next_rank, next_differentia):
                    child.InsertTaxon(
                        taxon_label,
                        rank_differentia_iter,
                    )
                    return
            else:
                TrieInnerNode(
                    next_rank, next_differentia, parent=self
                ).InsertTaxon(taxon_label, rank_differentia_iter)

        except StopIteration:
            TrieLeafNode(parent=self, taxon_label=taxon_label)

    def InsertCachedTaxon(self: "TrieInnerNode", taxon_label: str) -> None:
        self.InsertTaxon(taxon_label, self._cached_rditer)

    @property
    def taxon_label(self: "TrieInnerNode") -> str:
        if self.parent is None:
            return "Root"
        else:
            # numpy ints cause indexing errors; convert to native int
            return f"""Inner+r={self._rank}+d={
                render_to_base64url(int(self._rank))
            }"""

    @property
    def taxon(self: "TrieInnerNode") -> str:
        return self.name

    @property
    def origin_time(self: "TrieInnerNode") -> int:
        return opyt.or_value(self._rank, 0)

    @property
    def inner_children(self: "TrieInnerNode"):
        return filter(
            lambda child_: isinstance(child_, TrieInnerNode),
            self.children,
        )

    def __repr__(self: "TrieInnerNode"):
        return f"""(rank {
            self._rank
        }, diff {
            self._differentia
        }) @ {
            render_to_base64url(id(self) % 8192)
        }"""
