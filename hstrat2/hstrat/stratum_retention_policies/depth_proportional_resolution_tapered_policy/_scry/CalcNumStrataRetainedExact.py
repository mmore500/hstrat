import typing

from ..PolicySpec import PolicySpec
from .._impl import calc_provided_uncertainty


class CalcNumStrataRetainedExact:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "CalcNumStrataRetainedExact",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(
        self: "CalcNumStrataRetainedExact",
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcNumStrataRetainedExact",
        policy: "Policy",
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposted?"""

        spec = policy.GetSpec()
        guaranteed_resolution = spec._guaranteed_depth_proportional_resolution

        if num_strata_deposited < guaranteed_resolution * 2 + 1:
            return num_strata_deposited
        else:
            # must calculate whether there will be +1 due to retention of
            # most recently deposited stratum
            # (i.e., whether it overlaps with a rank from among
            # the 2 * resolution pegs)
            subtrahend = 2 * guaranteed_resolution + 1
            shifted = num_strata_deposited - subtrahend
            divisor = 2 * guaranteed_resolution - 1
            # equivalent int(math.floor(math.log(shifted // divisor + 1, 2)))
            # cast to int to handle numpy.int32, numpy.int64, etc.
            exp = int(shifted // divisor + 1).bit_length() - 1
            modulus = 2**exp
            bump = (num_strata_deposited - 1) % modulus != 0

            return 2 * guaranteed_resolution + bump
