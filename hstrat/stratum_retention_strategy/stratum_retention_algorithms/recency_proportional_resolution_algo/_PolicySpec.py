import typing

from .._detail import PolicySpecBase


class PolicySpec(PolicySpecBase):
    """Contains all policy parameters, if any."""

    _recency_proportional_resolution: int

    def __init__(
        self: "PolicySpec",
        recency_proportional_resolution: int,
    ) -> None:
        """Construct the policy spec.

        Parameters
        ----------
        recency_proportional_resolution : int, optional
            The desired minimum number of intervals between the MRCA and the
            deeper compared column to be able to be distinguished between. The
            uncertainty of MRCA rank estimates provided under the MRCA-recency-
            proportional resolution policy will scale as the actual
            phylogenetic depth of the MRCA divided by
            recency_proportional_resolution.
        """
        self._recency_proportional_resolution = recency_proportional_resolution

    def __eq__(self: "PolicySpec", other: typing.Any) -> bool:
        return isinstance(other, self.__class__) and (
            self._recency_proportional_resolution,
        ) == (other._recency_proportional_resolution,)

    def __repr__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoIdentifier()
        }.{
            PolicySpec.__qualname__
        }(recency_proportional_resolution={
            self._recency_proportional_resolution
        })"""

    def __str__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoTitle()
        } (resolution: {
            self._recency_proportional_resolution
        })"""

    def GetEvalCtor(self: "PolicySpec") -> str:
        return f"hstrat.{self!r}"

    def GetRecencyProportionalResolution(self: "PolicySpec") -> int:
        return self._recency_proportional_resolution

    @staticmethod
    def GetAlgoIdentifier() -> str:
        """Get programatic name for underlying retention algorithm."""
        return __package__.split(".")[-1]

    @staticmethod
    def GetAlgoTitle() -> str:
        """Get human-readable name for underlying retention algorithm."""
        return "Recency-proportional Resolution Stratum Retention Algorithm"
