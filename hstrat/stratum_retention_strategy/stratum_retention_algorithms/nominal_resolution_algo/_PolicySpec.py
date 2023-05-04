import typing

from .._detail import PolicySpecBase


class PolicySpec(PolicySpecBase):
    """Contains all policy parameters, if any."""

    def __eq__(self: "PolicySpec", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __repr__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoIdentifier()
        }.{
            PolicySpec.__qualname__
        }()"""

    def __str__(self: "PolicySpec") -> str:
        return self.GetAlgoTitle()

    def GetEvalCtor(self: "PolicySpec") -> str:
        return f"hstrat.{self!r}"

    @staticmethod
    def GetAlgoIdentifier() -> str:
        """Get programatic name for underlying retention algorithm."""
        return __package__.split(".")[-1]

    @staticmethod
    def GetAlgoTitle() -> str:
        """Get human-readable name for underlying retention algorithm."""
        return "Nominal Resolution Stratum Retention Algorithm"
