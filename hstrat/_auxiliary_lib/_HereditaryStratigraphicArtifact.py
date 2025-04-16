import typing

if typing.TYPE_CHECKING:
    from ..frozen_instrumentation import HereditaryStratigraphicSpecimen
    from ..genome_instrumentation import (
        HereditaryStratigraphicColumn,
        HereditaryStratigraphicSurface,
    )

HereditaryStratigraphicArtifact = typing.Union[
    "HereditaryStratigraphicColumn",
    "HereditaryStratigraphicSurface",
    "HereditaryStratigraphicSpecimen",
]
