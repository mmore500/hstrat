import typing

import mpmath as mp

from ._calc_common_ratio import calc_common_ratio


def calc_target_recency(
    degree: int,
    pow_: int,
    num_strata_deposited: int,
) -> typing.Union[float, mp.mpf]:
    """ "What should the target recency of the `pow`'th exponentially
    distributed coverage target be when `num_strata_deposited`?

    Will strictly increase with `num_strata_deposited`.
    """
    common_ratio = calc_common_ratio(degree, num_strata_deposited)
    try:
        res = common_ratio**pow_
    except OverflowError:
        res = mp.mpf(common_ratio) ** pow_
    return res
