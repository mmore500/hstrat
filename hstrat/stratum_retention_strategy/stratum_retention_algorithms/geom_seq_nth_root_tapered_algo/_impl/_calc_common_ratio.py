import typing
import warnings

import mpmath as mp


def calc_common_ratio(
    degree: int,
    num_strata_deposited: int,
) -> typing.Union[float, mp.mpf]:
    """What should the base of the exponential distribution of retained
    ranks be?"""
    # this try-except isn't necessary for the test cases
    # and the bounds of normal usage, but provides better resiliency
    # for extreme magnitude num_strata_deposited which may arise from time
    # to time due to trickle down to this function from within a doubling
    # search
    # the mpf type (artibtrary-precision floating-point) will propagate
    # forward through subsequent computations
    try:
        num_strata_deposited = float(num_strata_deposited)
    except OverflowError:
        warnings.warn(
            "OverflowError converting num_strata_deposited to float, "
            "converting to mpmath.mpf instead.",
        )
        num_strata_deposited = mp.mpf(num_strata_deposited)

    # base ** degree == num_strata_deposited
    # take the degree'th root of each side...
    return num_strata_deposited ** (1 / degree)
