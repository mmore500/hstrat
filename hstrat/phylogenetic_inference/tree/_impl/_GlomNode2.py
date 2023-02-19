import functools
from iterpop import iterpop as ip
import itertools as it
import logging
import numbers
import statistics
import typing

import anytree
import numpy as np
import opytional as opyt
import sortedcontainers as sc

from ...._auxiliary_lib import (
    assign_intersecting_subsets,
    deep_listify,
    flat_len,
    generate_omission_subsets,
    intersect_ranges,
    pairwise,
)
from ....genome_instrumentation import HereditaryStratigraphicColumn
from ....juxtaposition import (
    calc_rank_of_first_retained_disparity_between,
    calc_rank_of_last_retained_commonality_among,
    calc_rank_of_last_retained_commonality_between,
)
from ....stratum_retention_viz import (
    col_to_ascii,
)
from ...pairwise import (
    calc_rank_of_mrca_bounds_between,
    estimate_patristic_distance_between,
    estimate_rank_of_mrca_between,
    estimate_ranks_since_mrca_with,
)

confidence_level = 0.49


def validate(func):
    @functools.wraps(func)  # presever name, docstring, etc
    def wrapper(self, *args, **kwargs):  # NOTE: no self
        self.Validate()
        retval = func(
            self, *args, **kwargs
        )  # call original function or method
        self.Validate()
        return retval

    return wrapper


class GlomNode2(anytree.NodeMixin):

    _leaves: sc.SortedList

    def __init__(self: "GlomNode", parent=None, children=None) -> None:
        self.parent = parent

        self._leaves = sc.SortedList(
            key=lambda node: node.GetNumStrataDeposited(),
        )  # leaves, sorted with youngest first and oldest last

        if children:
            self.children = children
            for child in children:
                self._leaves.update(child._leaves)

    @property
    def shortrep(self):
        return self._leaves[0]

    @property
    def longrep(self):
        return self._leaves[-1]

    # def GetFirstRetainedDisparityBetween(self, node):
    #
    #     return (
    #         calc_rank_of_first_retained_disparity_between(
    #             self._leaves[0], col, confidence_level=confidence_level
    #         )
    #         or self._leaves[0].GetNumStrataDeposited()
    # )

    def GetFirstRetainedDisparityWithShort(self, col):
        # logging.debug(col_to_ascii(col))
        # logging.debug(col_to_ascii(self._leaves[0]))
        logging.debug(f"first retained disp short {id(self._leaves[0])}")
        return (
            calc_rank_of_first_retained_disparity_between(
                self._leaves[0], col, confidence_level=confidence_level
            )
            or self._leaves[0].GetNumStrataDeposited()
        )

    def GetFirstRetainedDisparityWithLong(self, col):
        # logging.debug(col_to_ascii(col))
        # logging.debug(col_to_ascii(self._leaves[-1]))
        logging.debug(f"first retained disp long {id(self._leaves[-1])}")
        return (
            calc_rank_of_first_retained_disparity_between(
                self._leaves[-1], col, confidence_level=confidence_level
            )
            or self._leaves[-1].GetNumStrataDeposited()
        )

    def GetLastRetainedCommonalityWithShort(self, col):
        # logging.debug(col_to_ascii(col))
        # logging.debug(col_to_ascii(self._leaves[0]))
        logging.debug(f"last retained common short {id(self._leaves[0])}")
        return calc_rank_of_last_retained_commonality_between(
            self._leaves[0], col, confidence_level=confidence_level
        )

    def GetLastRetainedCommonalityWithLong(self, col):
        # logging.debug(col_to_ascii(col))
        # logging.debug(col_to_ascii(self._leaves[-1]))
        logging.debug(f"last retained common long {id(self._leaves[-1])}")
        return calc_rank_of_last_retained_commonality_between(
            self._leaves[-1], col, confidence_level=confidence_level
        )

    def GetLastRetainedCommonalityWithDeep(self, col):
        # logging.debug(col_to_ascii(col))
        # logging.debug(col_to_ascii(self._leaves[-1]))
        return self.FindBestMatch(col)

    def GetFirstRetainedDisparityWithDeep(self, col):
        # logging.debug(col_to_ascii(col))
        # logging.debug(col_to_ascii(self._leaves[-1]))
        return self.FindBestStreak(col)

    # @validate
    def PercolateColumn(self, col):
        logging.debug(f"{id(self)} percolating {id(col)}")

        # add first leaf
        if len(self._leaves) == 0:
            self._leaves.add(col)
            self.Validate()
            logging.debug(f"{id(self)} added first leaf")
            return

        # make first split
        if len(self._leaves) == 1:
            GlomNode2(parent=self).PercolateColumn(
                ip.popsingleton(self._leaves)
            )
            self._leaves.add(col)
            logging.debug(f"{id(self)} made first split")
            GlomNode2(parent=self).PercolateColumn(col)
            return

        assert len(self.children) >= 2, len(self.children)
        # forward to best-matching branch
        first_disparities = [
            child.GetFirstRetainedDisparityWithDeep(col)
            for child in self.children
        ]
        # last_commonalities = [
        #     child.GetLastRetainedCommonalityWithLong(col)
        #     for child in self.children
        # ]

        zip_ = [
            *zip(
                self.children,
                [*map(anytree.LevelOrderIter, self.children)],
                deep_listify(generate_omission_subsets(first_disparities)),
            )
        ]
        while True:
            continue_ = False
            for child, candidate_, other_disparities in zip_:
                candidate = next(candidate_, None)
                if (
                    candidate is not None
                    and candidate.GetLastRetainedCommonalityWithDeep(col)
                    >= max(other_disparities)
                    # >= max(max(other_disparities), max(other_commonalities) + 1)
                ):
                    self._leaves.add(col)
                    logging.debug(f"{id(self)} forwarded to best branch")
                    logging.debug(f"{max(other_disparities)} max other_disparities")
                    logging.debug(f"{candidate.GetLastRetainedCommonalityWithLong(col)}")
                    logging.debug(f"other_disparities {other_disparities}")
                    logging.debug(f"chose {id(child)}")
                    child.PercolateColumn(col)
                    return
                elif candidate is not None:
                    continue_ = True

            if not continue_:
                logging.debug("best branch search exhausted")
                break

        logging.debug("best match forwarding failed")

        # shim insertion
        to_push = set()
        for child_idx1, child_idx2 in it.combinations(
            range(len(self.children)), r=2
        ):
            child1 = self.children[child_idx1]
            child2 = self.children[child_idx2]
            # TODO
            if child1.GetLastRetainedCommonalityWithShort(
                child2.shortrep
            ) >= max(
                # if child1.GetLastRetainedCommonalityWithLong(
                #     child2.longrep
                # ) >= max(
                child1.GetFirstRetainedDisparityWithLong(col),
                child2.GetFirstRetainedDisparityWithLong(col),
            ):
                to_push.add(child_idx1)
                to_push.add(child_idx2)

        if to_push:
            if len(to_push) == len(self.children):
                GlomNode2(parent=self, children=self.children)
                GlomNode2(parent=self).PercolateColumn(col)
                self._leaves.add(col)
            else:
                GlomNode2(
                    parent=self,
                    children=tuple(self.children[i] for i in to_push),
                )
                self.PercolateColumn(col)

            logging.debug(f"{id(self)} inserted shim")
            return

        # should this be what if multiple best?
        # if len(set(first_disparities)) != 1:
        #     youngest_disparity = max(first_disparities)
        #     self.

        logging.debug(f"{id(self)} created polytomy")
        GlomNode2(parent=self).PercolateColumn(col)
        self._leaves.add(col)

        logging.debug(f"{id(self)} fallthorugh")

    def GetBoundsWithShort(self, node):
        return (
            self.GetLastRetainedCommonalityWithShort(node.shortrep),
            self.GetFirstRetainedDisparityWithShort(node.shortrep),
        )

    def GetBoundsWithLong(self, node):
        return (
            self.GetLastRetainedCommonalityWithLong(node.longrep),
            self.GetFirstRetainedDisparityWithLong(node.longrep),
        )

    def GetBoundsIntersection(self: "GlomNode"):
        bounds = [
            c1.GetBoundsWithShort(c2) for c1, c2 in pairwise(self.children)
        ] + [c1.GetBoundsWithLong(c2) for c1, c2 in pairwise(self.children)]
        return intersect_ranges(bounds)

    def GetBoundsIntersectionShort(self: "GlomNode"):
        bounds = [
            c1.GetBoundsWithShort(c2) for c1, c2 in pairwise(self.children)
        ]
        return intersect_ranges(bounds)

    def GetBackpoint(self: "GlomNode"):
        short = min(
            calc_rank_of_first_retained_disparity_between(
                c1.shortrep, c2.shortrep
            )
            or min(c1.shortrep.GetNumStrataDeposited(), c2.shortrep.GetNumStrataDeposited())
            for c1, c2 in pairwise(self.children)
        )
        long = min(
            calc_rank_of_first_retained_disparity_between(
                c1.longrep, c2.longrep
            )
            or min(c1.longrep.GetNumStrataDeposited(), c2.longrep.GetNumStrataDeposited())
            for c1, c2 in pairwise(self.children)
        )
        return min(short, long) - 1

    def GetFrontpoint(self: "GlomNode"):
        # return min(
        #     calc_rank_of_first_retained_disparity_between(c1.shortrep, c2.shortrep, confidence_level=0.49) or 0
        #     for c1, c2 in pairwise(self.children)
        # )
        return min(
            calc_rank_of_last_retained_commonality_between(
                c1.shortrep, c2.shortrep, confidence_level=0.49
            )
            or 0
            for c1, c2 in pairwise(self.children)
        )

    # @functools.cached_property  # TODO just call from root
    @property
    def origin_time(self: "GlomNode"):
        logging.debug(f"{id(self)} calculating origin_time")
        if self.is_root:
            logging.debug(f"{id(self)} origin_time: root")
            return 0
        elif self.is_leaf:
            logging.debug(f"{id(self)} origin_time: leaf")
            assert len(self._leaves) == 1
            res = self._leaves[0].GetNumStrataDeposited() - 1
        # elif self.GetBoundsIntersection() is not None:
        #     logging.debug(f"{id(self)} origin_time: bounds intersection")
        #     assert len(self._leaves) > 1
        #     # res = self.GetBackpoint()
        #     # res = statistics.mean(*self.GetBoundsIntersection())
        #     res = self.GetBoundsIntersection()[1] - 1
        #     # res = self.GetBoundsIntersection()[0]
        # elif self.GetBoundsIntersectionShort() is not None:
        #     logging.debug(f"{id(self)} origin_time: bounds intersection short")
        #     res = self.GetBoundsIntersectionShort()[1] - 1
        elif True:
            res = min(
                opyt.or_value(calc_rank_of_first_retained_disparity_between(
                    l1, l2, confidence_level=confidence_level
                ), l1.GetNumStrataDeposited())
                for l1, l2 in it.combinations(self._leaves, r=2)
            ) - 1
        elif True:
            logging.debug(
                f"{id(self)} origin_time: bounds intersection frontpoint"
            )
            res = min(
                self.GetFrontpoint(),
                self.GetBackpoint(),
                min(child.origin_time for child in self.children),
            )
        else:
            print(self)
            for leaf in self._leaves:
                print(id(leaf))
                print(col_to_ascii(leaf))
            assert False
            logging.debug(f"{id(self)} origin_time: backpoint")
            return self.GetBackpoint()
        assert not np.isnan(res)
        assert res >= 0
        return res

    def Validate(self):
        if self.is_leaf:
            assert len(self._leaves) < 2, len(self._leaves)

        assert len(self._leaves) == len(self.leaves)

    def __str__(self: "GlomNode") -> str:
        return "\n".join(
            f"{pre} ({id(node)}) {node.name}"
            for pre, __, node in anytree.RenderTree(self)
        )
        # return "\n".join(
        #     f"{pre} ({id(node)}) {node.origin_time} {node.name}"
        #     for pre, __, node in anytree.RenderTree(self)
        # )

    @property
    def name(self: "GlomNode"):
        if len(self._leaves) == 1:
            return " ".join(map(str, map(id, self._leaves)))
        else:
            return ""

    def ResolveShims(self):
        last_commonalities = [
            max(
                self.children[child_idx1].GetLastRetainedCommonalityWithShort(
                    self.children[child_idx2].shortrep
                ),
                self.children[child_idx1].GetLastRetainedCommonalityWithLong(
                    self.children[child_idx2].longrep
                ),
            )
            for child_idx1, child_idx2 in it.combinations(
                range(len(self.children)), r=2
            )
        ]

        if len(set(last_commonalities)) == 1:
            return

        for child1 in self.children:
            to_push = set()
            for child2 in self.children:
                if child1 is not child2:
                    if child1.GetLastRetainedCommonalityWithShort(
                        child2.shortrep
                    ) == max(last_commonalities):
                        to_push.add(child1)
                        to_push.add(child2)
                    elif child1.GetLastRetainedCommonalityWithLong(
                        child2.longrep
                    ) == max(last_commonalities):
                        to_push.add(child1)
                        to_push.add(child2)

            # assert len(to_push) < len(self.children)
            if len(to_push) == len(self.children):
                continue
            if to_push:
                logging.debug(f"resolving shim {to_push}")
                GlomNode2(
                    parent=self,
                    children=tuple(to_push),
                )
                self.ResolveShims()
                return

    def FindBestMatch(self, col):
        if self.is_leaf:
            return calc_rank_of_last_retained_commonality_between(
                self._leaves[0], col, confidence_level=confidence_level
            )

        # first_disparities = [
        #     child.GetLastRetainedCommonalityWithLong(col)
        #     for child in self.children
        # ]
        # max_ = max(first_disparities)
        return max(
            child.FindBestMatch(col)
            for child in self.children
            # for d, child in zip(first_disparities, self.children)
            # if d == max_
        )


    def FindBestStreak(self, col):
        if self.is_leaf:
            res = calc_rank_of_first_retained_disparity_between(
                self._leaves[0], col, confidence_level=confidence_level
            )
            if res is None:
                return self._leaves[0].GetNumStrataDeposited()
            else:
                return res

        # first_disparities = [
        #     child.GetLastRetainedCommonalityWithLong(col)
        #     for child in self.children
        # ]
        # max_ = max(first_disparities)
        return max(
            child.FindBestStreak(col)
            for child in self.children
            # for d, child in zip(first_disparities, self.children)
            # if d == max_
        )
