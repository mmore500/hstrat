import typing

from .._detail import PolicySpecBase


class PolicySpec(PolicySpecBase):
    """Contains all policy parameters, if any."""

    _retention_probability: float

    def __init__(
        self: "PolicySpec",
        *,
        retention_probability: float = 0.5,
    ) -> None:
        """Construct the policy spec.

        Parameters
        ----------
        retention_probability : float
            The proability with which strata are retained permanently.
        """
        self._retention_probability = retention_probability

    def __eq__(self: "PolicySpec", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __repr__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoIdentifier()
        }.{
            PolicySpec.__qualname__
        }(retention_probability={
            self._retention_probability
        })"""

    def __str__(self: "PolicySpec") -> str:
        return self.GetAlgoTitle()

    def GetEvalCtor(self: "PolicySpec") -> str:
        return f"""hstrat.{self!r}"""

    def GetRetentionProbability(self: "PolicySpec") -> int:
        return self._retention_probability

    @staticmethod
    def GetAlgoIdentifier() -> str:
        """Get programatic name for underlying retention algorithm."""
        return __package__.split(".")[-1]

    @staticmethod
    def GetAlgoTitle() -> str:
        """Get human-readable name for underlying retention algorithm."""
        return "Stochastic Stratum Retention Algorithm"
