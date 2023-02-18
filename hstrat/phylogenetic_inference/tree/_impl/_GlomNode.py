import itertools as it
import logging
import numbers
import statistics
import typing

import anytree
import opytional as opyt
import sortedcontainers as sc

from ...._auxiliary_lib import (
    assign_intersecting_subsets,
    flat_len,
    intersect_ranges,
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


def calc_rank_of_first_retained_disparity_between_(c1, c2):
    return opyt.or_value(
        calc_rank_of_first_retained_disparity_between(
            c1, c2, confidence_level=confidence_level
        ),
        c1.GetNumStrataDeposited(),
    )


def calc_rank_of_last_retained_commonality_between_(c1, c2):
    return opyt.or_value(
        calc_rank_of_last_retained_commonality_between(
            c1, c2, confidence_level=confidence_level
        ),
        0,
    )


class GlomNode(anytree.NodeMixin):

    _leaves: sc.SortedSet
    origin_time: numbers.Real

    def __init__(self: "GlomNode", origin_time=None, parent=None, children=None):
        # if parent:
        #     assert origin_time >= parent.origin_time
        self.origin_time = origin_time
        self.parent = parent
        self._leaves = sc.SortedList(
            key=lambda node: node.GetNumStrataDeposited(),
        )  # leaves, sorted with youngest first and oldest last

        if children:
            self.children = children
            for child in children:
                self._leaves.update(child._leaves)

        if origin_time is not None:
            self.origin_time = origin_time
        if self._leaves:
            self.UpdateOriginTime()

    @property
    def representative(self: "GlomNode"):
        return self._leaves[0]

    @property
    def longestrepresentative(self: "GlomNode"):
        return self._leaves[-1]

    @property
    def name(self: "GlomNode"):
        if len(self._leaves) == 1:
            return " ".join(map(str, map(id, self._leaves)))
        else:
            return ""

    def _PercolateColumn(
        self: "GlomNode", column: HereditaryStratigraphicColumn
    ) -> None:
        logging.debug(f"percolating column {id(column)}")

        first_disparities = [
            calc_rank_of_first_retained_disparity_between_(
                column, child.representative
            )
            for child in self.children
        ]
        last_commonalities = [
            calc_rank_of_last_retained_commonality_between_(
                column, child.representative
            )
            for child in self.children
        ]
        recentest_first_disparity = max(first_disparities or [None])
        recentest_last_commonality = max(last_commonalities or [None])
        patristic_distances = [
            estimate_patristic_distance_between(
                column, child.representative, "maximum_likelihood", "arbitrary"
            )
            for child in self.children
        ]
        rank_mrcas = [
            estimate_rank_of_mrca_between(
                column, child.representative, "maximum_likelihood", "arbitrary"
            )
            for child in self.children
        ]
        since_mrcas = [
            estimate_ranks_since_mrca_with(
                column, child.representative, "maximum_likelihood", "arbitrary"
            )
            for child in self.children
        ]
        since_mrcas2 = [
            estimate_ranks_since_mrca_with(
                child.representative, column, "maximum_likelihood", "arbitrary"
            )
            for child in self.children
        ]
        deposits = [
            child.representative.GetNumStrataDeposited()
            for child in self.children
        ]

        self._leaves.add(column)

        if len(self._leaves) == 1:
            logging.debug("initializing empty node")
            return
        elif (len(self.children)) == 1:
            # THIS CASE IS ONLY TEMPORARY AFTER SHIM INSERTION
            logging.debug("single child case")

            self.origin_time = calc_rank_of_last_retained_commonality_between_(
                self.children[0].representative,
                column,
            )
            child = GlomNode(
                origin_time=column.GetNumStrataDeposited() - 1,
                parent=self,
            )
            child.PercolateColumn(column)
            return
        elif len(self.children) == 0:
            logging.debug("performing first split")
            assert len(self._leaves) == 2
            self.origin_time = calc_rank_of_last_retained_commonality_between_(
                *self._leaves,
            )
            for leaf_col in self._leaves:
                child = GlomNode(
                    origin_time=leaf_col.GetNumStrataDeposited() - 1,
                    parent=self,
                )
                child.PercolateColumn(leaf_col)
            return

        else:
            assert len(self.children) > 1
            logging.debug("forwarding to most related child")
            descending_iters = [
                anytree.LevelOrderIter(child) for child in self.children
            ]
            win_thresholds = [
                max(first_disparities[:i] + first_disparities[i + 1 :])
                # max(first_disparities)
                for i in range(len(self.children))
            ]

            while True:
                continue_ = False
                for child, iter_, thresh in zip(
                    self.children,
                    descending_iters,
                    win_thresholds,
                ):
                    desc = next(iter_, None)
                    if desc is not None:
                        continue_ = True
                    if (
                        desc is not None
                        and calc_rank_of_last_retained_commonality_between_(
                            column, desc.representative
                        )
                        >= thresh
                    ):
                        logging.debug("identified child")
                        child.PercolateColumn(column)
                        return
                if not continue_:
                    break

        # polytomy
        # if len(set(last_commonalities)) == 1:
        if True:
            logging.debug("handling polytomy")
            logging.debug(f"first_disparities={first_disparities}")
            logging.debug(f"last_commonalities={last_commonalities}")
            logging.debug(f"patristic_distances={patristic_distances}")
            logging.debug(f"rank_mrcas={rank_mrcas}")
            logging.debug(f"since_mrcas={since_mrcas}")
            logging.debug(f"since_mrcas2={since_mrcas2}")
            logging.debug(f"deposits={deposits}")
            logging.debug(
                "column.GetNumStrataDeposited()="
                f"{column.GetNumStrataDeposited()}"
            )
            assert len(self.children) >= 2

            lrc = calc_rank_of_last_retained_commonality_among(
                (child.representative for child in self.children),
                confidence_level=confidence_level,
            )

            # this is probably wrong
            if lrc > max(last_commonalities):
                # self becomes shim node, then makes column its second child
                logging.debug("inserting shim node")
                logging.debug(f"self {id(self)} parent {id(self.parent)}")
                # assert lrc >= self.origin_time
                GlomNode(
                    origin_time=opyt.apply_if_or_value(
                        self.GetBoundsIntersection(),
                        lambda x: x[0],
                        lrc,
                    ),
                    parent=self,
                    children=self.children,
                )

            # assert self.origin_time >= min(last_commonalities)
            self.origin_time = min(last_commonalities)
            child = GlomNode(
                origin_time=column.GetNumStrataDeposited() - 1,
                parent=self,
            )
            child.PercolateColumn(column)
            if self.GetBoundsIntersection() is None:
                self.ResolveFracture()
            self.UpdateOriginTime()
            self.Checkup()
            assert len(child._leaves)
            logging.debug(f"coming back up through node {id(self)}")

        # # these sections need consideration
        # elif first_disparities.count(recentest_first_disparity) == 1:
        #     logging.debug("forwarding to most related child")
        #     assert last_commonalities.count(recentest_last_commonality) == 1
        #
        #     recentest_first_disparity_idx = first_disparities.index(
        #         recentest_first_disparity
        #     )
        #     recentest_last_commonality_idx = last_commonalities.index(
        #         recentest_last_commonality
        #     )
        #     assert (
        #         recentest_first_disparity_idx == recentest_last_commonality_idx
        #     )
        #
        #     self.children[recentest_first_disparity_idx].PercolateColumn(
        #         column
        #     )
        # elif last_commonalities.count(recentest_last_commonality) == 1:
        #     logging.debug("forwarding to most related child")
        #     assert False
        #
        #     recentest_last_commonality_idx = last_commonalities.index(
        #         recentest_last_commonality
        #     )
        #
        #     self.children[recentest_last_commonality_idx].PercolateColumn(
        #         column
        #     )
        # else:
        #     logging.debug("resolving partial polytomy")
        #     logging.debug(f"first_disparities={first_disparities}")
        #     logging.debug(f"last_commonalities={last_commonalities}")
        #
        #     # todo generalize
        #     assert False

        # TOOD go down both equivalent sides of tree and look for evidence otherwise create a new branch directly

    def GetMegaBoundsIntersection(
        self: "GlomNode",
    ) -> typing.Optional[typing.Tuple[numbers.Integral, numbers.Integral]]:
        bounds = [
            calc_rank_of_mrca_bounds_between(
                c1, c2, prior="arbitrary", confidence_level=confidence_level
            )
            for child1, child2 in it.combinations(self.children, r=2)
            for c1, c2 in it.product(child1._leaves, child2._leaves)
        ]
        return intersect_ranges(bounds)

    def GetBoundsIntersection(
        self: "GlomNode",
    ) -> typing.Optional[typing.Tuple[numbers.Integral, numbers.Integral]]:
        bounds = [
            calc_rank_of_mrca_bounds_between(
                c1.representative,
                c2.representative,
                prior="arbitrary",
                confidence_level=confidence_level,
                strict=False,
            )
            for c1, c2 in it.combinations(self.children, r=2)
        ]
        return intersect_ranges(bounds)

    def HasValidOriginTime(self: "GlomNode") -> bool:
        bi = self.GetBoundsIntersection()
        if bi is not None:
            lb, ub = bi
            return lb <= self.origin_time < ub
        else:
            # TODO generalize
            # assert (
            #     self.origin_time
            #     == self._leaves[0].GetNumStrataDeposited() - 1
            # ), (
            #     self.origin_time, len(self._leaves)
            # )
            pass

        return True

    def HasValidMegaBoundsIntersection(self: "GlomNode") -> bool:
        return (self.GetMegaBoundsIntersection() is not None) or len(
            self._leaves
        ) <= 1

    def HasValidBoundsIntersection(self: "GlomNode") -> bool:
        return (self.GetBoundsIntersection() is not None) or len(
            self.children
        ) <= 1

    def ResolveFracture(self: "GlomNode", cl = 0.49) -> None:
        print("boo")
        bounds = [
            calc_rank_of_mrca_bounds_between(
                c1.representative,
                c2.representative,
                prior="arbitrary",
                confidence_level=confidence_level,
            )
            for c1, c2 in it.combinations(self.children, r=2)
        ]
        partition = assign_intersecting_subsets(bounds)

        blame = [*it.combinations(range(len(self.children)), r=2)]

        assert len(partition) > 1

        assert len(partition) == 2  # handle more general case later
        # assert flat_len(partition) == 6  # handle more general case later

        gang = {
            indiv for combo_id in partition[-1] for indiv in blame[combo_id]
        }

        gang_nodes = [self.children[i] for i in gang]
        # gang_time = calc_rank_of_last_retained_commonality_among(
        #     (n.representative for n in gang_nodes),
        #     confidence_level=confidence_level,
        # )
        # assert gang_time is not None

        print(partition, bounds, len(self.children))
        print("self", id(self))
        print("blame", blame)
        print("gang", gang)
        for g in gang:
            print(id(self.children[g].representative))
            print(col_to_ascii(self.children[g].representative))

        # +----------------------------------------------------+
        # |                    MOST ANCIENT                    |
        # +--------------+---------------+---------------------+
        # | stratum rank | stratum index | stratum differentia |
        # +--------------+---------------+---------------------+
        # |      0       |       0       |          0*         |
        # +--------------+---------------+---------------------+
        # |      1       |       1       |          0*         |
        # +--------------+---------------+---------------------+
        # |      2       |       2       |          1*         |
        # +--------------+---------------+---------------------+
        # |      3       |       3       |          1*         |
        # +--------------+---------------+---------------------+
        # |      4       |       4       |          1*         |
        # +--------------+---------------+---------------------+
        # |                    MOST RECENT                     |
        # +----------------------------------------------------+
        # +----------------------------------------------------+
        # |                    MOST ANCIENT                    |
        # +--------------+---------------+---------------------+
        # | stratum rank | stratum index | stratum differentia |
        # +--------------+---------------+---------------------+
        # |      0       |       0       |          0*         |
        # +--------------+---------------+---------------------+
        # |      1       |       1       |          0*         |
        # +--------------+---------------+---------------------+
        # |      2       |       2       |          1*         |
        # +--------------+---------------+---------------------+
        # |      3       |       3       |          0*         |
        # +--------------+---------------+---------------------+
        # |      4       |       4       |          1*         |
        # +--------------+---------------+---------------------+
        # |                    MOST RECENT                     |
        # +----------------------------------------------------+
        # +----------------------------------------------------+
        # |                    MOST ANCIENT                    |
        # +--------------+---------------+---------------------+
        # | stratum rank | stratum index | stratum differentia |
        # +--------------+---------------+---------------------+
        # |      0       |       0       |          0*         |
        # +--------------+---------------+---------------------+
        # |      1       | ░░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░░░░ |
        # +--------------+---------------+---------------------+
        # |      2       |       1       |          1*         |
        # +--------------+---------------+---------------------+
        # |      3       | ░░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░░░░ |
        # +--------------+---------------+---------------------+
        # |      4       |       2       |          1*         |
        # +--------------+---------------+---------------------+
        # |      5       |       3       |          1*         |
        # +--------------+---------------+---------------------+
        # |      6       |       4       |          0*         |
        # +--------------+---------------+---------------------+
        # |      7       |       5       |          1*         |
        # +--------------+---------------+---------------------+
        # |      8       |       6       |          0*         |
        # +--------------+---------------+---------------------+
        # |      9       |       7       |          1*         |
        # +--------------+---------------+---------------------+
        # |      10      |       8       |          1*         |
        # +--------------+---------------+---------------------+
        # |                    MOST RECENT                     |
        # +----------------------------------------------------+

        if len(gang) == len(self.children):
            # problem: one has missing strata
            # A   B   C
            # 1   1   1
            # 0   X   1
            # 1   1   1
            # etc.
            oddone = (
                max(gang, key=lambda x: self.children[x].representative.GetNumStrataDeposited())
            )
            oddone = self.children[oddone]
            oddone.parent = None
            for leaf in oddone._leaves:
                self.children[0].PercolateColumn(leaf)
            #
            #     # max(self.children, key=lambda x: calc_rank_of_last_retained_commonality_between_(x.longestrepresentative, leaf))
            #
            #     for child in self.children:
                    # child.PercolateColumn(leaf)
            return

        assert len(gang) < len(self.children)
        # assert self.origin_time <= gang_time

        x = GlomNode(origin_time=None, parent=self, children=gang_nodes)
        x.UpdateOriginTime()

        if not self.HasValidBoundsIntersection():
            self.ResolveFracture()
        self.UpdateOriginTime()

    def PercolateColumn(
        self: "GlomNode", column: HereditaryStratigraphicColumn
    ) -> None:

        logging.debug(f"PERCOLATING INSIDE {id(self)}")
        self._PercolateColumn(column)

        # if NOT intersecting, then split
        if not self.HasValidBoundsIntersection():
            self.ResolveFracture()

        # if not self.HasValidOriginTime():
        self.UpdateOriginTime()
        assert self.origin_time >= 0

        assert self.HasValidBoundsIntersection()
        assert self.HasValidOriginTime()
        # assert False
        # refactor
        # assert self.HasValidBoundsIntersection()
        # assert self.HasValidMegaBoundsIntersection()

    def Checkup(self: "GlomNode") -> None:
        pass
        assert self.origin_time >= 0
        # assert not np.isnan(self.origin_time)

        assert self.HasValidBoundsIntersection(), self.GetBoundsIntersection()
        if not self.HasValidOriginTime():
            print(self.origin_time)
            print(self.GetBoundsIntersection())
            self.UpdateOriginTime()
            print(self.origin_time)
        assert self.HasValidOriginTime(), (
            self.origin_time, self.GetBoundsIntersection(),
            "self id", id(self),
        )

    def UpdateOriginTime(self: "GlomNode") -> None:
        self.origin_time = opyt.apply_if_or_value(
            self.GetBoundsIntersection(),
            # lambda x: statistics.mean([x[1] - 1, x[0]]),
            lambda x: x[1] - 1,
            # lambda x: x[1] - 1,
            self._leaves[0].GetNumStrataDeposited() - 1,
        )

    def BigCheckup(self: "GlomNode") -> None:
        pass
        # assert self.HasValidMegaBoundsIntersection(), ("big checkup",
        #     self.origin_time, self.GetMegaBoundsIntersection(),
        #     "self id", id(self),
        # )

    def __str__(self: "GlomNode") -> str:
        return "\n".join(
            f"{pre} ({id(node)}) {node.origin_time} {node.name}"
            for pre, __, node in anytree.RenderTree(self)
        )
