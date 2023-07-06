from ..... import _auxiliary_lib as auxlib


def calc_provided_uncertainty(
    depth_proportional_resolution: int,
    num_completed_stratum_depositions_since: int,
) -> int:
    """How many ranks forward should the next retained strata be spaced from a
    retained stratum `num_completed_stratum_depositions_since` ranks back in
    the hereditary stratigraphic column's history?

    Calls to this function lay out retained ranks stepwise, with the rank
    chosen from the preceeding call used to determine
    `num_completed_stratum_depositions_since` for the next call. The zeroth
    rank (i.e., most ancient rank) serves as the starting point for the first
    call.

    Note that the returned value actually corresponds to one more than the
    uncertainty with respect to calculating MRCA supposing two identically
    distributed columns. For example a return value of 1 corresponds to
    strata retained at every rank, so the rank of the MRCA can be
    determined with 0 uncertainty.
    """
    guaranteed_resolution = depth_proportional_resolution
    max_uncertainty = (
        num_completed_stratum_depositions_since // guaranteed_resolution
    )

    # round down to lower or equal power of 2
    provided_uncertainty = auxlib.bit_floor(max_uncertainty) or 1
    return provided_uncertainty
