import typing
import warnings

from .._detail import PolicySpecBase


class PolicySpec(PolicySpecBase):
    """Contains all policy parameters, if any."""

    _size_curb: int

    def __init__(
        self: "PolicySpec",
        size_curb: int,
    ) -> None:
        """Construct the policy spec.

        Parameters
        ----------
        size_curb : int, optional
            Fixed, hard-limited stratum storage capacity to make best use of.

            Inclusive. Only size caps of eight strata and above are guaranteed
            respected. (Initialization of smaller size caps will warn.)
        """
        self._size_curb = size_curb
        if size_curb < 8:
            warnings.warn(
                f"Size curb set to {size_curb}, "
                "the minimum guaranteeable size limit is 8.",
            )

    def __eq__(self: "PolicySpec", other: typing.Any) -> bool:
        return isinstance(other, self.__class__) and (self._size_curb,) == (
            other._size_curb,
        )

    def __repr__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoIdentifier()
        }.{
            PolicySpec.__qualname__
        }(size_curb={
            self._size_curb
        })"""

    def __str__(self: "PolicySpec") -> str:
        return f"""{
            self.GetAlgoTitle()
        } (size_curb: {
            self._size_curb
        })"""

    def GetEvalCtor(self: "PolicySpec") -> str:
        return f"hstrat.{self!r}"

    def GetSizeCurb(self: "PolicySpec") -> int:
        return self._size_curb

    @staticmethod
    def GetAlgoIdentifier() -> str:
        """Get programatic name for underlying retention algorithm."""
        return __package__.split(".")[-1]

    @staticmethod
    def GetAlgoTitle() -> str:
        """Get human-readable name for underlying retention algorithm."""
        return "Curbed Recency-proportional Resolution Stratum Retention Algorithm"
