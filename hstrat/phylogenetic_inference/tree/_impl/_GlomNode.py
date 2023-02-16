import numbers

import anytree
import sortedcontainers as sc

from ....genome_instrumentation import HereditaryStratigraphicColumn
from ....juxtaposition import (
    calc_rank_of_first_retained_disparity_between,
    calc_rank_of_last_retained_commonality_between,
)
from ...pairwise import (
    estimate_patristic_distance_between,
    estimate_rank_of_mrca_between,
    estimate_ranks_since_mrca_with,
)


class GlomNode(anytree.NodeMixin):

    _leaves: sc.SortedSet
    origin_time: numbers.Real

    def __init__(self: "GlomNode", origin_time, parent=None, children=None):
        if parent:
            assert origin_time >= parent.origin_time
        self.origin_time = origin_time
        self.parent = parent
        self._leaves = sc.SortedList(
            key=lambda node: node.GetNumStrataDeposited(),
        )  # leaves, sorted with youngest first and oldest last

        if children:
            self.children = children
            for child in children:
                self._leaves.update(child._leaves)

    @property
    def representative(self: "GlomNode"):
        return self._leaves[0]

    @property
    def name(self: "GlomNode"):
        return " ".join(map(str, map(id, self._leaves)))

    def PercolateColumn(
        self: "GlomNode", column: HereditaryStratigraphicColumn
    ) -> None:
        self._leaves.add(column)
        if len(self._leaves) == 1:
            print("init")
            return

        first_disparities = [
            calc_rank_of_first_retained_disparity_between(
                column, child.representative
            )
            for child in self.children
        ]
        last_commonalities = [
            calc_rank_of_last_retained_commonality_between(
                column, child.representative
            )
            for child in self.children
        ]
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

        if len(self.children) == 0:
            print("first split")
            assert len(self._leaves) == 2
            self.origin_time = calc_rank_of_last_retained_commonality_between(
                *self._leaves,
            )
            for leaf_col in self._leaves:
                child = GlomNode(
                    origin_time=leaf_col.GetNumStrataDeposited() - 1,
                    parent=self,
                )
                child.PercolateColumn(leaf_col)
            return

        # polytomy
        if len(set(first_disparities)) == 1:
            assert len(set(last_commonalities)) == 1
            assert len(self.children) >= 2
            print("polytomy", first_disparities, last_commonalities)
            print("polytomy", patristic_distances, rank_mrcas)
            print("polytomy", since_mrcas, since_mrcas2)
            print("polytomy", deposits, column.GetNumStrataDeposited())

            lrc = calc_rank_of_last_retained_commonality_between(
                self.children[0].representative,
                self.children[1].representative,
            )

            if lrc > last_commonalities[0]:
                print("shim")
                assert lrc >= self.origin_time
                shim = GlomNode(
                    origin_time=lrc, parent=self, children=self.children
                )

            print("doing")
            assert self.origin_time >= last_commonalities[0]
            self.origin_time = last_commonalities[0]
            child = GlomNode(
                origin_time=column.GetNumStrataDeposited() - 1,
                parent=self,
            )
            child.PercolateColumn(column)
            assert len(child._leaves)
            return

        print("descend one")
        recentest_first_disparity = max(first_disparities)
        recentest_last_commonality = max(last_commonalities)

        # todo generalize
        assert first_disparities.count(recentest_first_disparity) == 1
        assert last_commonalities.count(recentest_last_commonality) == 1

        recentest_first_disparity_idx = first_disparities.index(
            recentest_first_disparity
        )
        recentest_last_commonality_idx = last_commonalities.index(
            recentest_last_commonality
        )
        assert recentest_first_disparity_idx == recentest_last_commonality_idx

        self.children[recentest_first_disparity_idx].PercolateColumn(column)
