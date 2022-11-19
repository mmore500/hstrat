import typing

from ....._auxiliary_lib import popcount
from ..._detail import PolicyCouplerBase
from .._PolicySpec import PolicySpec


class CalcNumStrataRetainedExact:
    """Functor to provide member function implementation in Policy class."""

    def __init__(
        self: "CalcNumStrataRetainedExact",
        policy_spec: typing.Optional[PolicySpec],
    ) -> None:
        pass

    def __eq__(self: "CalcNumStrataRetainedExact", other: typing.Any) -> bool:
        return isinstance(other, self.__class__)

    def __call__(
        self: "CalcNumStrataRetainedExact",
        policy: PolicyCouplerBase,
        num_strata_deposited: int,
    ) -> int:
        """Exactly how many strata are retained after n deposited?

        The calculation can be written mathematically as,

          weight of binary expansion of n (i.e., #1's set in binary repr)
          + sum(
              floor( log2(n//r) )
              for r from 1 to r inclusive
          )
          + 1

        where

          n = num_strata_deposited - 1
          r = resolution

        This expression for exact number deposited was extrapolated from
            * resolution = 0, <https://oeis.org/A063787>
            * resolution = 1, <https://oeis.org/A056791>
        and is unit tested extensively.

        Note that the implementation must include a special case to account for
        n < r causing log2(0). In this case, the number of strata retained is
        equal to the number deposited (i.e., none have been discarded yet).
        """
        spec = policy.GetSpec()

        resolution = spec.GetRecencyProportionalResolution()
        if num_strata_deposited - 1 <= resolution:
            return num_strata_deposited
        else:
            return (
                # cast to int to handle numpy.int32, numpy.int64 etc.
                popcount(int(num_strata_deposited - 1))
                + sum(
                    # X.bit_length() - 1 equivalent to floor(log2(X))
                    # cast to int to handle numpy.int32, numpy.int64 etc.
                    int((num_strata_deposited - 1) // r).bit_length() - 1
                    for r in range(1, resolution + 1)
                )
                + 1
            )
