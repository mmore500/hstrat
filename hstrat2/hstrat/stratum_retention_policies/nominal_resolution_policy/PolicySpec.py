import typing


class PolicySpec:
    """Contains all policy parameters, if any."""

    def __eq__(
        self: 'PolicySpec',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)
