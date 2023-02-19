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
        return (
            calc_rank_of_first_retained_disparity_between(
                self._leaves[0], col, confidence_level=confidence_level
            )
            or self._leaves[0].GetNumStrataDeposited()
        )

    def GetFirstRetainedDisparityWithLong(self, col):
        return (
            calc_rank_of_first_retained_disparity_between(
                self._leaves[-1], col, confidence_level=confidence_level
            )
            or self._leaves[-1].GetNumStrataDeposited()
        )

    def GetLastRetainedCommonalityWithShort(self, col):
        return calc_rank_of_last_retained_commonality_between(
            self._leaves[0], col, confidence_level=confidence_level
        )

    def GetLastRetainedCommonalityWithLong(self, col):
        return calc_rank_of_last_retained_commonality_between(
            self._leaves[-1], col, confidence_level=confidence_level
        )

    @validate
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
            GlomNode2(parent=self).PercolateColumn(col)
            logging.debug(f"{id(self)} made first split")
            return

        assert len(self.children) >= 2, len(self.children)
        # forward to best-matching branch
        first_disparities = [
            child.GetFirstRetainedDisparityWithLong(col)
            for child in self.children
        ]

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
                    and candidate.GetLastRetainedCommonalityWithLong(col)
                    >= max(other_disparities)
                ):
                    self._leaves.add(col)
                    child.PercolateColumn(col)
                    logging.debug(f"{id(self)} forwarded to best branch")
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
        return min(
            calc_rank_of_last_retained_commonality_between(
                c1.shortrep, c2.shortrep
            )
            or 0
            for c1, c2 in pairwise(self.children)
        )

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

    @functools.cached_property  # TODO just call from root
    # @property
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
            logging.debug(
                f"{id(self)} origin_time: bounds intersection frontpoint"
            )
            res = min(
                self.GetFrontpoint(),
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

    def __str__(self: "GlomNode") -> str:
        # return "\n".join(
        #     f"{pre} ({id(node)}) {node.name}"
        #     for pre, __, node in anytree.RenderTree(self)
        # )
        return "\n".join(
            f"{pre} ({id(node)}) {node.origin_time} {node.name}"
            for pre, __, node in anytree.RenderTree(self)
        )

    @property
    def name(self: "GlomNode"):
        if len(self._leaves) == 1:
            return " ".join(map(str, map(id, self._leaves)))
        else:
            return ""
