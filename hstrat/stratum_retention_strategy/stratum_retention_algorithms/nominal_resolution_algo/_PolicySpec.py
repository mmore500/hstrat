import typing

from .._detail import PolicySpecBase


class PolicySpec(PolicySpecBase):
    """Contains all policy parameters, if any."""

    def __eq__(self: "PolicySpec", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __repr__(self: "PolicySpec") -> str:
        return f"""{
            self.GetPolicyName()
        }.{
            PolicySpec.__qualname__
        }()"""

    def __str__(self: "PolicySpec") -> str:
        return self.GetPolicyTitle()

    @staticmethod
    def GetPolicyName() -> str:
        """Get programatic name for policy."""
        return __package__.split(".")[-1]

    @staticmethod
    def GetPolicyTitle() -> str:
        """Get human-readable title for policy."""
        return "Nominal Resolution Stratum Retention Policy"
