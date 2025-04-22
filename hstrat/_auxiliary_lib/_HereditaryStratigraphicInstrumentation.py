import typing

if typing.TYPE_CHECKING:  # False at runtime
    from ..genome_instrumentation import (
        HereditaryStratigraphicColumn,
        HereditaryStratigraphicSurface,
    )

HereditaryStratigraphicInstrumentation = typing.Union[
    "HereditaryStratigraphicColumn",
    "HereditaryStratigraphicSurface",
]

HereditaryStratigraphicInstrumentation_T = typing.TypeVar(
    "HereditaryStratigraphicInstrumentation_T",  # name
    "HereditaryStratigraphicColumn",  # constraints
    "HereditaryStratigraphicSurface",
)
