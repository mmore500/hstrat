import functools


@functools.lru_cache()
def calc_provided_degree(
    size_curb: int,
    interspersal: int,
    num_stratum_depositions_completed: int,
) -> int:
    """After n strata have been deposited, what degree is provided?"""
    # size_limit_inclusive = degree * 2 * (interspersal + 1) + 2
    # degree = (size_limit_inclusive - 2) / (2 * interspersal + 2)
    res = max(
        (size_curb - 2) // (2 * interspersal + 2),
        1,
    )

    # sanity check for policy self-consistency of transition from rpra to gsnra
    # when transferring, resolution 0 is provided, which will be pow2 spacing
    assert res <= int(num_stratum_depositions_completed).bit_length()

    return res
