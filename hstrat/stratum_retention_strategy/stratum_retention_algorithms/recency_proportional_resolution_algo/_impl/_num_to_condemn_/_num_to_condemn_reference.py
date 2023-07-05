def num_to_condemn_reference(
    recency_proportional_resolution: int,
    num_stratum_depositions_completed: int,
) -> int:
    """How many strata should be eliminated after
    num_stratum_depositions_completed have been deposited and the
    num_stratum_depositions_completed + 1'th deposition is in progress?

    Used to implement functor's __call__ method specifying which ranks should
    be purged during this stratum deposition. This expression for exact number
    deposited was extrapolated from
        * resolution = 0, <https://oeis.org/A001511>
        * resolution = 1, <https://oeis.org/A091090>
    and is unit tested extensively.
    """
    resolution = recency_proportional_resolution

    if num_stratum_depositions_completed % 2 == 1:
        return 0
    elif num_stratum_depositions_completed < 2 * (resolution + 1):
        return 0
    else:
        return 1 + num_to_condemn_reference(
            resolution,
            num_stratum_depositions_completed // 2,
        )
