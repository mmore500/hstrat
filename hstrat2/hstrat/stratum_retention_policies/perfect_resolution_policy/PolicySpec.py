import typing


class PolicySpec:

    def __eq__(
        self: 'PolicySpec',
        other: typing.Any,
    ):
        return type(self) is type(other)
