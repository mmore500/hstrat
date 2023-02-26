import functools
import itertools as it
import typing

import anytree
import numconv
import opytional as opyt

from ...._auxiliary_lib import HereditaryStratigraphicArtifact


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
    def taxon(self: "TrieInnerNode") -> str:
        return self.name

    @property
    def origin_time(self: "TrieInnerNode") -> int:
        return self.parent.origin_time


def iter_alignment(
    first: "TrieInnerNode", second: "TrieInnerNode"
) -> typing.Iterator[int]:
    for second_child in second.inner_children:
        for child in sorted(first.inner_children, key=lambda x: x._rank):
            if child.MatchesNode(second_child):
                yield child._rank
                yield from iter_alignment(child, second_child)


def iter_monotonic(iter_) -> typing.Iterator[int]:
    max_ = float("-inf")
    for v in iter_:
        if v > max_:
            yield v
            max_ = v


def _compete_alignment(
    first: "TrieInnerNode",
    seconds: typing.List["TrieInnerNode"],
    second_iters,  # must be iter_monotonic
) -> "TrieInnerNode":
    assert len(seconds)
    assert all(isinstance(x, TrieInnerNode) for x in seconds)

    idx_best = 0
    best = float("-inf")
    for vs in it.zip_longest(*second_iters):
        num_nones = sum((v is None) for v in vs)
        # don't need this case: zip_longest -> not all Nones
        # if num_nones == len(vs):
        #     return idx_best
        if num_nones == len(vs) - 1 and vs[idx_best] is not None:
            return seconds[idx_best]
        for idx, v in enumerate(vs):
            if v is not None and v >= best:
                idx_best = idx
                best = v

    return seconds[idx_best]


def iter_descent(node: "TrieInnerNode"):
    while True:
        yield node
        if node.children:
            (node,) = node.children
        else:
            return


def compete_alignment(
    first: "TrieInnerNode",
    seconds: typing.List["TrieInnerNode"],
) -> "TrieInnerNode":
    assert len(seconds)
    assert all(isinstance(x, TrieInnerNode) for x in seconds)
    return _compete_alignment(
        first,
        seconds,
        [iter_monotonic(iter_alignment(first, second)) for second in seconds],
    )


# def do_rezip(
#     first: "TrieInnerNode", second: "TrieInnerNode"
# ) -> None:
#     # second guaranteed to be linked list NOT IT ISNT
#     if second.children:
#         second_child, = second.children
#     else:
#         second.parent = first.parent
#         return
#
#     for child in sorted(first.chldren, key=lambda x: x._rank):
#         if child.MatchesNode(second_child):
#             do_rezip(child, second_child)
#             return


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

    def Matches(
        self: "TrieInnerNode",
        rank: int,
        differentia: int,
    ) -> bool:
        return self._rank == rank and self._differentia == differentia

    def MatchesNode(
        self: "TrieInnerNode",
        other: "TrieInnerNode",
    ) -> bool:
        return self.Matches(other._rank, other._differentia)

    def HasDescendant(
        self: "TrieInnerNode",
        rank: int,
        differentia: int,
    ) -> bool:
        if rank < self._rank:
            return False
        elif rank == self._rank and differentia == self._differentia:
            return True
        else:
            return any(
                child.HasDescendant(rank, differentia)
                for child in self.children
            )

    def GetDescendants(
        self: "TrieInnerNode",
        rank: int,
        differentia: int,
    ) -> typing.Iterator["TrieInnerNode"]:
        if rank == self._rank and differentia == self._differentia:
            return iter([self])
        elif rank > self._rank:
            return it.chain(
                *[
                    child.GetDescendants(rank, differentia)
                    for child in self.children
                    if isinstance(child, TrieInnerNode)
                ]
            )
        else:
            return iter([])

    def InsertTaxon(
        self: "TrieInnerNode",
        taxon_label: str,
        rank_differentia_iter,
    ) -> None:
        try:
            next_rank, next_differentia = next(rank_differentia_iter)
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
            # reverse=True,  # from most ancient to least ancient
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
