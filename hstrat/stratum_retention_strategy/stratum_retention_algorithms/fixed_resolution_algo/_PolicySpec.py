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
            self.GetAlgoIdentifier()
        }.{
            PolicySpec.__qualname__
        }(fixed_resolution={
            self._fixed_resolution
        })"""

    def __str__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoTitle()
        } (resolution: {
            self._fixed_resolution
        })"""

    def GetEvalCtor(self: "PolicySpec") -> str:
        return f"hstrat.{self!r}"

    def GetFixedResolution(self: "PolicySpec") -> int:
        return self._fixed_resolution

    @staticmethod
    def GetAlgoIdentifier() -> str:
        """Get programatic name for underlying retention algorithm."""
        return __package__.split(".")[-1]

    @staticmethod
    def GetAlgoTitle() -> str:
        """Get human-readable name for underlying retention algorithm."""
        return "Fixed Resolution Stratum Retention Algorithm"
