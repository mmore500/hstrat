import copy
import functools
import itertools as it
import random
import typing

import anytree
import opytional as opyt

from ...._auxiliary_lib import generate_n, render_to_base64url
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

    def FindGenesesOfAllele(
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
                yield from child.FindGenesesOfAllele(rank, differentia)
        elif rank == self._rank and differentia == self._differentia:
            yield self
        elif rank > self._rank:
            for child in self.inner_children:
                yield from child.FindGenesesOfAllele(rank, differentia)

    def GetDeepestConsecutiveSharedAlleleGenesis(
        self: "TrieInnerNode",
        taxon_allele_genesis_iter: typing.Iterator[typing.Tuple[int, int]],
    ) -> (
        typing.Tuple["TrieInnerNode", typing.Iterator[typing.Tuple[int, int]]]
    ):
        # iterator must be copyable
        assert [*copy.copy(taxon_allele_genesis_iter)] == [
            *copy.copy(taxon_allele_genesis_iter)
        ]

        node_stack = [self]
        allele_genesis_stack = [taxon_allele_genesis_iter]
        deepest_genesis = self
        deepest_taxon_allele_genesis_iter = copy.copy(
            taxon_allele_genesis_iter
        )
        while True:

            candidate_genesis = node_stack.pop()
            taxon_allele_genesis_iter = allele_genesis_stack.pop()

            if (
                opyt.or_value(candidate_genesis._rank, -1),
                candidate_genesis._tiebreaker,
            ) > (
                opyt.or_value(deepest_genesis._rank, -1),
                deepest_genesis._tiebreaker,
            ):
                deepest_genesis = candidate_genesis
                deepest_taxon_allele_genesis_iter = copy.copy(
                    taxon_allele_genesis_iter
                )

            next_allele = next(taxon_allele_genesis_iter, None)
            if next_allele is not None:
                node_stack.extend(
                    candidate_genesis.FindGenesesOfAllele(*next_allele)
                )
                allele_genesis_stack.extend(
                    generate_n(
                        lambda: copy.copy(taxon_allele_genesis_iter),
                        len(node_stack) - len(allele_genesis_stack),
                    )
                )

            assert len(node_stack) == len(allele_genesis_stack)
            if not node_stack:
                break

        return deepest_genesis, deepest_taxon_allele_genesis_iter

    def InsertTaxon(
        self: "TrieInnerNode",
        taxon_label: str,
        taxon_allele_genesis_iter: typing.Iterator[typing.Tuple[int, int]],
    ) -> None:
        try:
            # common allele genesis trace is for special condition optimization
            # where GetDeepestConsecutiveSharedAlleleGenesis isn't needed
            next_rank, next_differentia = next(taxon_allele_genesis_iter)
            assert next_rank is not None
            assert next_differentia is not None
            for child in self.inner_children:
                if child.Matches(next_rank, next_differentia):
                    child.InsertTaxon(
                        taxon_label,
                        taxon_allele_genesis_iter,
                    )
                    return
            else:
                TrieInnerNode(
                    next_rank, next_differentia, parent=self
                ).InsertTaxon(taxon_label, taxon_allele_genesis_iter)

        except StopIteration:
            TrieLeafNode(parent=self, taxon_label=taxon_label)

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
