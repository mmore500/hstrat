import typing
import warnings

from .._detail import PolicySpecBase


class PolicySpec(PolicySpecBase):
    """Contains all policy parameters, if any."""

    _degree: int
    _interspersal: int

    def __init__(
        self: "PolicySpec",
        degree: int,
        interspersal: int = 2,
    ) -> None:
        """Construct the policy spec.

        Parameters
        ----------
        degree : int
            How many should target recencies for uncertainty-capped coverage
            should be spaced exponentially from zero recency to maximum recency
            (i.e., number strata deposited)? Adjust this parameter to set upper
            bound on space complexity (i.e., to ensure available space is not
            exceeded).
        interspersal : int
            At least how many retained ranks should be spaced between zero
            recency and each target recency? Must be greater than 0. No bound
            on MRCA rank estimate uncertainty provided if set to 1. For most
            use cases, leave this set to 2.
        """
        assert degree >= 0
        assert interspersal >= 1
        if interspersal == 1:
            warnings.warn(
                "Interspersal set to 1, "
                "no bound on MRCA rank estimate uncertainty can be guaranteed.",
            )
        self._degree = degree
        self._interspersal = interspersal

    def __eq__(self: "PolicySpec", other: typing.Any) -> bool:
        return isinstance(other, self.__class__) and (
            self._degree,
            self._interspersal,
        ) == (
            other._degree,
            other._interspersal,
        )

    def __repr__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoIdentifier()
        }.{
            PolicySpec.__qualname__
        }(degree={
            self._degree
        }, interspersal={
            self._interspersal
        })"""

    def __str__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoTitle()
        } (degree: {
            self._degree
        }, interspersal: {
            self._interspersal
        })"""

    def GetEvalCtor(self: "PolicySpec") -> str:
        return f"hstrat.{self!r}"

    def GetDegree(self: "PolicySpec") -> int:
        return self._degree

    def GetInterspersal(self: "PolicySpec") -> int:
        return self._interspersal

    @staticmethod
    def GetAlgoIdentifier() -> str:
        """Get programatic name for underlying retention algorithm."""
        return __package__.split(".")[-1]

    @staticmethod
    def GetAlgoTitle() -> str:
        """Get human-readable name for underlying retention algorithm."""
        return "Nth Root Geometric Sequence Stratum Retention Algorithm"
