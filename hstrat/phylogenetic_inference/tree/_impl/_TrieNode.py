import copy
import functools
import itertools as it
import typing

import anytree
import numconv
import opytional as opyt

from ...._auxiliary_lib import CopyableSeriesItemsIter


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
            id(self) % 1024
        :x}"""


def iter_alignment(
    first: "TrieInnerNode",  # zipto: will be missing elenets/older
    second: "TrieInnerNode",
) -> typing.Iterator[int]:
    if first.ConflictsNode(second):
        return
    elif first.MatchesNode(second):
        yield first._rank
        for x, y in it.product(first.inner_children, second.inner_children):
            yield from iter_alignment(x, y)
    elif first._rank > second._rank:
        for y in second.inner_children:
            yield from iter_alignment(first, y)
    elif first._rank < second._rank:
        for x in first.inner_children:
            yield from iter_alignment(x, second)
    else:
        assert False


def iter_monotonic(iter_) -> typing.Iterator[int]:
    max_ = float("-inf")
    for v in iter_:
        if v > max_:
            yield v
            max_ = v


def _compete_alignment(
    first: "TrieInnerNode",  # zipto
    second_iters,  # must be iter_monotonic
) -> int:
    idx_best = 0
    best = -1
    for vs in it.zip_longest(*second_iters):
        num_nones = sum((v is None) for v in vs)
        # don't need this case: zip_longest -> not all Nones
        # if num_nones == len(vs):
        #     return idx_best
        if num_nones == len(vs) - 1 and vs[idx_best] is not None:
            assert best >= 0 or len(vs) == 1
            return idx_best
        for idx, v in enumerate(vs):
            if v is not None and v >= best:
                idx_best = idx
                best = v

    assert best >= 0
    return idx_best


def compete_alignment(
    first: "TrieInnerNode",
    seconds: typing.List["TrieInnerNode"],
) -> "TrieInnerNode":
    assert len(seconds)
    assert all(isinstance(x, TrieInnerNode) for x in seconds)
    return seconds[
        _compete_alignment(
            first,
            [
                iter_monotonic(iter_alignment(first, second))
                for second in seconds
            ],
        )
    ]


class TrieInnerNode(anytree.NodeMixin):

    _rank: int
    _differentia: int

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

    def Matches(
        self: "TrieInnerNode",
        rank: int,
        differentia: int,
    ) -> bool:
        return self._rank == rank and self._differentia == differentia

    def Conflicts(
        self: "TrieInnerNode",
        rank: int,
        differentia: int,
    ) -> bool:
        return self._rank == rank and self._differentia != differentia

    def MatchesNode(
        self: "TrieInnerNode",
        other: "TriInnerNode",
    ) -> bool:
        return self.Matches(other._rank, other._differentia)

    def ConflictsNode(
        self: "TrieInnerNode",
        other: "TrieInnerNode",
    ) -> bool:
        return self.Conflicts(other._rank, other._differentia)

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
        depth=0,
    ) -> typing.Optional["TrieInnerNode"]:
        # print("depth", depth)
        self._cached_rditer = copy.copy(rank_differentia_iter)
        self._cached_depth = depth
        try:
            next_rank, next_differentia = next(rank_differentia_iter)
        except StopIteration:
            return None
        candidates = self.GetDescendants(next_rank, next_differentia)
        # print(
        #     next_rank,
        #     next_differentia,
        #     self._rank,
        #     self._differentia,
        #     candidates,
        # )
        return max(
            sorted(  # instead of sort, pick max based on tuple with tiebreaker
                (opyt.or_value(
                    candidate.GetDeepestAlignment(
                        copy.copy(rank_differentia_iter),
                        depth + 1,
                    ),
                    candidate,
                )
                for candidate in candidates),
                key=id,
            ),
            default=None,
            key=lambda x: x._cached_depth,
            # key=lambda x: x[0],
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

    def ConsolidateChildren(self: "TrieInnerNode"):
        for __, clump in it.groupby(
            sorted(
                self.inner_children, key=lambda x: (x._rank, x._differentia)
            ),
            key=lambda x: (x._rank, x._differentia),
        ):
            clump = [*clump]
            assert len(clump) <= 2
            if len(clump) == 2:
                copy1, copy2 = clump
                for child in copy2.children:
                    child.parent = copy1
                copy2.parent = None
                copy1.ConsolidateChildren()

    # not recursive; call from top to bottom externally
    def Rezip(self: "TrieInnerNode"):
        if not self.children:
            return

        sorted_children = sorted(
            self.inner_children,
            key=lambda x: x._rank,
            # reverse=True,  # from most recent to most ancient?
        )
        for idx, zipto in enumerate(sorted_children):
            candidates = [
                descendant
                for child_ in sorted_children
                if child_ is not zipto
                for descendant in child_.GetDescendants(
                    zipto._rank, zipto._differentia
                )
            ]
            if not candidates:
                # print("no candidates")
                continue

            assert all(isinstance(x, TrieInnerNode) for x in candidates)
            assert all(
                candidate._rank == zipto._rank for candidate in candidates
            )
            assert all(
                candidate._differentia == zipto._differentia
                for candidate in candidates
            )
            # print(self)
            # print(f"{zipto=}")
            # print(f"{candidates=}")
            winner = compete_alignment(zipto, candidates)
            # print(f"{winner=}")
            # perform rezip
            for child_ in zipto.children:
                child_.parent = winner
            zipto.parent = None

            winner.ConsolidateChildren()

    @property
    def name(self: "TrieInnerNode") -> str:
        if self.parent is None:
            return "RootNode"
        else:
            return f"""Inner+r={self._rank}+d={
                numconv.int2str(self._differentia, 64, numconv.BASE64URL)
            }"""

    @property
    def taxon_label(self: "TrieInnerNode") -> str:
        return self.name

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

    def __str__(self: "TrieInnerNode"):
        return f"""(rank {
            self._rank
        }, diff {
            self._differentia
        }) @ {
            id(self) % 1024
        :x}"""

    def __repr__(self: "TrieInnerNode"):
        return str(self)

    @property
    def name(self: "TrieInnerNode"):
        return str(self)
