import typing

from .._detail import PolicySpecBase


class PolicySpec(PolicySpecBase):
    """Contains all policy parameters, if any."""

    def __eq__(self: "PolicySpec", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __repr__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoName()
        }.{
            PolicySpec.__qualname__
        }()"""

    def __str__(self: "PolicySpec") -> str:
        return self.GetAlgoTitle()

    @staticmethod
    def GetAlgoName() -> str:
        """Get programatic name for underlying retention algorithm."""
        return __package__.split(".")[-1]

    @staticmethod
    def GetAlgoTitle() -> str:
        """Get human-readable title for policy."""
        return "Perfect Resolution Stratum Retention Algorithm"
