import typing


class PolicySpec:
    """Contains all policy parameters, if any."""

    def __eq__(
        self: 'PolicySpec',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __repr__(
        self: 'PolicySpec',
    ) -> str:
        return f'''{
            __package__.split(".")[-1]
        }.{
            PolicySpec.__qualname__
        }()'''
