import typing

from .._detail import PolicySpecBase


class PolicySpec(PolicySpecBase):
    """Contains all policy parameters, if any."""

    _guaranteed_depth_proportional_resolution: int

    def __init__(
        self: "PolicySpec",
        guaranteed_depth_proportional_resolution: int,
    ):
        """Construct the policy spec.

        Parameters
        ----------
        guaranteed_depth_proportional_resolution : int
            The desired minimum number of intervals for the rank of the MRCA to
            be able to be distinguished between. The uncertainty of MRCA
            rank estimates provided under the depth-proportional resolution
            policy will scale as total number of strata deposited divided by
            guaranteed_depth_proportional_resolution.
        """

        assert guaranteed_depth_proportional_resolution > 0
        self._guaranteed_depth_proportional_resolution = (
            guaranteed_depth_proportional_resolution
        )

    def __eq__(self: "PolicySpec", other: typing.Any) -> bool:
        return isinstance(other, self.__class__) and (
            self._guaranteed_depth_proportional_resolution,
        ) == (other._guaranteed_depth_proportional_resolution,)

    def __repr__(self: "PolicySpec") -> str:
        return f"""{
            self.GetPolicyName()
        }.{
            PolicySpec.__qualname__
        }(guaranteed_depth_proportional_resolution={
            self._guaranteed_depth_proportional_resolution
        })"""

    def __str__(self: "PolicySpec") -> str:
        return f"""{
            self.GetPolicyTitle()
        } (resolution: {
            self._guaranteed_depth_proportional_resolution
        })"""

    @staticmethod
    def GetPolicyName() -> str:
        return __package__.split(".")[-1]

    @staticmethod
    def GetPolicyTitle() -> str:
        return "Depth-proportional Resolution Stratum Retention Policy"
