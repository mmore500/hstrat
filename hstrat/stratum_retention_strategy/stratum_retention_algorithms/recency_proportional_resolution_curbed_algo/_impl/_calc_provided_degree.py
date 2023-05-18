import functools


@functools.lru_cache()
def calc_provided_degree(
    size_curb: int,
    interspersal: int,
    num_stratum_depositions_completed: int,
) -> int:
    """After m strata have been deposited, what geometric sequence nth root
    algorithm degree n is provided?"""
    # size_limit_inclusive = degree * 2 * (interspersal + 1) + 2
    # degree = (size_limit_inclusive - 2) / (2 * interspersal + 2)
    res = max(
        (size_curb - 2) // (2 * interspersal + 2),
        1,
    )

    return res
