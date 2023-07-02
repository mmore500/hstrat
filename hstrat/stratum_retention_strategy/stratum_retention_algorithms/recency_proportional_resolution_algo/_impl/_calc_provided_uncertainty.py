from ..... import _auxiliary_lib as auxlib


def calc_provided_uncertainty(
    recency_proportional_resolution: int,
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
    resolution = recency_proportional_resolution

    max_uncertainty = num_stratum_depositions_completed // (resolution + 1)
    # round down to lower or equal power of 2
    provided_uncertainty = auxlib.bit_floor(max_uncertainty) or 1
    return provided_uncertainty
