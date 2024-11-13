from __future__ import annotations

from random import randint
import typing

from hstrat import hstrat
from hstrat.genome_instrumentation import HereditaryStratigraphicColumn


class Genome:
    __slots__ = ["annotation", "data"]

    def __init__(
        self,
        data: typing.Optional[typing.List[int]] = None,
        annotation: typing.Optional[HereditaryStratigraphicColumn] = None,
    ) -> None:
        self.data = data or [randint(1, 100)]
        self.annotation = annotation or HereditaryStratigraphicColumn(
            stratum_retention_policy=hstrat.recency_proportional_resolution_algo.Policy(
                8
            ),
            stratum_differentia_bit_width=8,
        )

    def get_descendant(self) -> Genome:
        return Genome(
            self.data + [randint(1, 100)], self.annotation.CloneDescendant()
        )

    @property
    def score(self) -> int:  # weighted average, more recent preferred
        n = len(self.data)
        return sum(sum(self.data[i:]) for i in range(n)) * 2 // (n * (n - 1))


def simulate_evolution(
    parents: typing.List[Genome], *, generations: int, carrying_capacity: int
) -> typing.List[Genome]:
    for _ in range(generations):
        children = sum(
            [[p.get_descendant() for p in parents] for _ in range(3)], []
        )
        children.sort(key=lambda x: x.score)
        parents = children[-carrying_capacity:]
    return parents
