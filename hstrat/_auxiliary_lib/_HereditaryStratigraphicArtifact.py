import typing

# use string alias due to circular module initialization issue
HereditaryStratigraphicArtifact = typing.Union[
    "HereditaryStratigraphicColumn",  # noqa: F821
    "HereditaryStratigraphicSpecimen",  # noqa: F821
]
