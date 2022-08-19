import typing

from .._detail import PolicySpecBase


class PolicySpec(PolicySpecBase):
    """Contains all policy parameters, if any."""

    _fixed_resolution: int

    def __init__(
        self: "PolicySpec",
        fixed_resolution: int,
    ):
        """Construct the policy spec.

        Parameters
        ----------
        fixed_resolution : int
            The rank interval strata should be retained at. The uncertainty of
            MRCA estimates provided under the fixed resolution policy will
            always be strictly less than this cap.
        """
        assert fixed_resolution > 0
        self._fixed_resolution = fixed_resolution

    def __eq__(self: "PolicySpec", other: typing.Any) -> bool:
        return isinstance(other, self.__class__) and (
            self._fixed_resolution,
        ) == (other._fixed_resolution,)

    def __repr__(self: "PolicySpec") -> str:
        return f"""{
            self.GetPolicyName()
        }.{
            PolicySpec.__qualname__
        }(fixed_resolution={
            self._fixed_resolution
        })"""

    def __str__(self: "PolicySpec") -> str:
        return f"""{
            self.GetPolicyTitle()
        } (resolution: {
            self._fixed_resolution
        })"""

    @staticmethod
    def GetPolicyName() -> str:
        """Get programatic name for policy."""
        return __package__.split(".")[-1]

    @staticmethod
    def GetPolicyTitle() -> str:
        return "Fixed Resolution Stratum Retention Policy"
