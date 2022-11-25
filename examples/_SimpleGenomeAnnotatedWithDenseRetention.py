import random
import typing

import opytional as opyt

from hstrat import hstrat


class SimpleGenomeAnnotatedWithDenseRetention:

    content: float
    annotation: hstrat.HereditaryStratigraphicColumn

    def __init__(
        self: "SimpleGenomeAnnotatedWithDenseRetention",
        content_: typing.Optional[float] = None,
        annotation_: typing.Optional[
            hstrat.HereditaryStratigraphicColumn
        ] = None,
    ) -> None:
        self.content = opyt.or_value(
            content_,
            random.uniform(0, 100),
        )
        self.annotation = opyt.or_value(
            annotation_,
            hstrat.HereditaryStratigraphicColumn(
                hstrat.fixed_resolution_algo.Policy(4),
            ),
        )

    def CreateOffspring(
        self: "SimpleGenomeAnnotatedWithDenseRetention",
    ) -> "SimpleGenomeAnnotatedWithDenseRetention":
        return SimpleGenomeAnnotatedWithDenseRetention(
            self.content + random.uniform(0.0, 1.0) % 100.0,
            self.annotation.CloneDescendant(),
        )
