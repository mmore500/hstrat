import typing

if typing.TYPE_CHECKING:  # False at runtime
    from ..genome_instrumentation import (
        HereditaryStratigraphicColumn,
        HereditaryStratigraphicSurface,
    )

# using TypeVar as opposed to Union constrains multiple
# instances of the annotation in the same signature to be
# of the same type
# (e.g., must all be HereditaryStratigraphicColumn or
# all be HereditaryStratigraphicSurface)
HereditaryStratigraphicInstrument = typing.TypeVar(
    "HereditaryStratigraphicInstrument",  # name
    "HereditaryStratigraphicColumn",  # constraints
    "HereditaryStratigraphicSurface",
)
