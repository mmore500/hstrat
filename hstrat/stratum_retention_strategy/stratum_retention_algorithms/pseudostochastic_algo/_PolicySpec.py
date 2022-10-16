import typing

from .._detail import PolicySpecBase


class PolicySpec(PolicySpecBase):
    """Contains all policy parameters, if any."""

    hash_salt: int

    def __init__(self: "PolicySpec", hash_salt: int) -> None:
        """Construct the policy spec.

        Parameters
        ----------
        hash_salt : int
            Salt value fed into hash used to deterministically choose whether
            to keep or drop ranks.
        """
        self._hash_salt = hash_salt

    def __eq__(self: "PolicySpec", other: typing.Any) -> bool:
        return isinstance(other, self.__class__) and (self._hash_salt,) == (
            other._hash_salt,
        )

    def __repr__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoIdentifier()
        }.{
            PolicySpec.__qualname__
        }(hash_salt={
            self._hash_salt
        })"""

    def __str__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoTitle()
        } (hash salt: {
            self._hash_salt
        })"""

    def GetHashSalt(self: "PolicySpec") -> int:
        return self._hash_salt

    def GetEvalCtor(self: "PolicySpec") -> str:
        return f"hstrat.{self!r}"

    @staticmethod
    def GetAlgoIdentifier() -> str:
        """Get programatic name for underlying retention algorithm."""
        return __package__.split(".")[-1]

    @staticmethod
    def GetAlgoTitle() -> str:
        """Get human-readable name for underlying retention algorithm."""
        return "Pseudostochastic Stratum Retention Algorithm"
