import typing

from .._detail import PolicySpecBase


class PolicySpec(PolicySpecBase):
    """Contains all policy parameters, if any."""

    _depth_proportional_resolution: int

    def __init__(
        self: "PolicySpec",
        depth_proportional_resolution: int,
    ):
        """Construct the policy spec.

        Parameters
        ----------
        depth_proportional_resolution : int
            The desired minimum number of intervals for the rank of the MRCA to
            be able to be distinguished between. The uncertainty of MRCA
            rank estimates provided under the tapered depth-proportional
            resolution policy will scale as total number of strata deposited
            divided by depth_proportional_resolution.
        """
        assert depth_proportional_resolution > 0
        self._depth_proportional_resolution = depth_proportional_resolution

    def __eq__(self: "PolicySpec", other: typing.Any) -> bool:
        return isinstance(other, self.__class__) and (
            self._depth_proportional_resolution,
        ) == (other._depth_proportional_resolution,)

    def __repr__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoIdentifier()
        }.{
            PolicySpec.__qualname__
        }(depth_proportional_resolution={
            self._depth_proportional_resolution
        })"""

    def __str__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoTitle()
        } (resolution: {
            self._depth_proportional_resolution
        })"""

    def GetEvalCtor(self: "PolicySpec") -> str:
        return f"hstrat.{self!r}"

    def GetDepthProportionalResolution(self: "PolicySpec") -> int:
        return self._depth_proportional_resolution

    @staticmethod
    def GetAlgoIdentifier() -> str:
        """Get programatic name for underlying retention algorithm."""
        return __package__.split(".")[-1]

    @staticmethod
    def GetAlgoTitle() -> str:
        """Get human-readable name for underlying retention algorithm."""
        return (
            "Tapered Depth-proportional Resolution Stratum Retention Algorithm"
        )
