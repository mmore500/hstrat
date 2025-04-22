import typing

if typing.TYPE_CHECKING:
    from ..frozen_instrumentation import HereditaryStratigraphicSpecimen
    from ..genome_instrumentation import (
        HereditaryStratigraphicColumn,
        HereditaryStratigraphicSurface,
    )

# using TypeVar as opposed to Union constrains multiple
# instances of the annotation in the same signature to be
# of the same type
# (e.g., must all be HereditaryStratigraphicColumn or
# all be HereditaryStratigraphicSurface)
HereditaryStratigraphicArtifact = typing.TypeVar(
    "HereditaryStratigraphicArtifact",  # name
    "HereditaryStratigraphicColumn",  # constraints
    "HereditaryStratigraphicSurface",
    "HereditaryStratigraphicSpecimen",
)
