import typing

from ._calc_common_ratio import calc_common_ratio


def iter_target_recencies(
    degree: int,
    num_strata_deposited: int,
) -> typing.Iterator[int]:
    """Yield strata recencies for each exponentially-spaced coverage target
    `pow` in ascending order."""
    # target recencies are a geometric sequence
    common_ratio = calc_common_ratio(degree, num_strata_deposited)
    # don't iterate over 0th pow, this is just the most recent rank
    # i.e., recency == 1
    for pow_ in range(1, degree + 1):
        yield common_ratio**pow_
