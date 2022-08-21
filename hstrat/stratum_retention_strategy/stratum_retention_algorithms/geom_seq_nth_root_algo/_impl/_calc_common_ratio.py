def calc_common_ratio(
    degree: int,
    num_strata_deposited: int,
) -> float:
    """What should the base of the exponential distribution of retained
    ranks be?"""
    # base ** degree == num_strata_deposited
    # take the degree'th root of each side...
    return num_strata_deposited ** (1 / degree)
