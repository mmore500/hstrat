def calc_provided_resolution(
    size_curb: int,
    num_stratum_depositions_completed: int,
) -> int:
    """After n strata have been deposited, what resolution is provided?

    Resolution may be negative, indicating that geom seq nth root should be
    used.
    """
    # (resolution + 1) * log2(num_stratum_depositions_completed) <= size_curb
    # (resolution + 1) * ceil(log2(num_depositons)) == size_curb
    # resolution + 1 == size_curb / ceil(log2(num_depositons))
    # resolution = size_curb / ceil(log2(num_depositons)) - 1
    res = (
        size_curb
        // (
            # int cast allows for other integer-like types i.e., np int64 etc
            int(num_stratum_depositions_completed).bit_length()
            + 1
        )
        - 1
    )

    # ensure necessary ranks for consistent transition to
    # geometric sequence nth root algorithm
    # this threshold also used in calc_geom_seq_nth_root_transition_rank
    resolution_thresh = 2
    assert resolution_thresh >= 0

    if res < resolution_thresh:
        return -1
    else:
        return res
