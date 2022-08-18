def calc_provided_uncertainty(
    guaranteed_depth_proportional_resolution: int,
    num_stratum_depositions_completed: int,
) -> int:
    """After n strata have been deposited, how many ranks are spaced
    between retained strata?

    Note that the returned value actually corresponds to one more than the
    uncertainty with respect to calculating MRCA supposing two identically
    distributed columns. For example a return value of 1 corresponds to
    strata retained at every rank, so the rank of the MRCA can be
    determined with 0 uncertainty.
    """

    guaranteed_resolution = guaranteed_depth_proportional_resolution
    max_uncertainty = (
        num_stratum_depositions_completed // guaranteed_resolution
    )

    # round down to lower or equal power of 2
    # cast to int to make robust to numpy.int32, numpy.int64, etc.
    provided_uncertainty_exp = int(max_uncertainty // 2).bit_length()
    provided_uncertainty = 2**provided_uncertainty_exp
    return provided_uncertainty
