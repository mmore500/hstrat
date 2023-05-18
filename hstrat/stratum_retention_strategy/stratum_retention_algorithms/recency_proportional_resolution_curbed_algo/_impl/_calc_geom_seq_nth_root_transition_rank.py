def calc_geom_seq_nth_root_transition_rank(size_curb: int) -> int:
    """What is the first rank where recency-proportional resolution algorithm
    sunsets and geometric sequence nth root algorithm applies?

    Return value zero implies that recency-proportional resolution algorithm
    never applies and geometric sequence nth root algorithm is used throughout
    deposition sequence.
    """
    # resolution_thresh threshold chosen to ensure availability of ranks
    # required by geometric sequence nth root algorithm at transion point
    # see calc_provided_resolution, where equivalent threshold also applies
    resolution_thresh = 2
    assert resolution_thresh >= 0
    return 2 ** (size_curb // (resolution_thresh + 1)) // 2
