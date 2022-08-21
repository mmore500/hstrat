import typing

from .._detail import PolicySpecBase


class PolicySpec(PolicySpecBase):
    """Contains all policy parameters, if any."""

    random_seed: int

    def __init__(self: "PolicySpec", random_seed: int) -> None:
        """Construct the policy spec.

        Parameters
        ----------
        random_seed : int
            Seed value for the onboard random number generator.
        """
        self._random_seed = random_seed

    def __eq__(self: "PolicySpec", other: typing.Any) -> bool:
        return isinstance(other, self.__class__) and (self._random_seed,) == (
            other._random_seed,
        )

    def __repr__(self: "PolicySpec") -> str:
        return f"""{
            self.GetPolicyName()
        }.{
            __package__.split(".")[-1]
        }(random_seed={
            self._random_seed
        })"""

    def __str__(self: "PolicySpec") -> str:
        return f"""{
            self.GetPolicyTitle()
        } (seed: {
            self._random_seed
        })"""

    @staticmethod
    def GetPolicyName() -> str:
        """Get programatic name for policy."""
        return __package__.split(".")[-1]

    @staticmethod
    def GetPolicyTitle() -> str:
        """Get human-readable title for policy."""
        return "Pseudostochastic Stratum Retention Policy"
