def calc_geom_seq_nth_root_transition_rank(size_curb: int) -> int:
    """Rank where gsnra first appears. Rank before is last before gsnra."""
    resolution_thresh = 2
    return 2 ** (size_curb // (resolution_thresh + 1)) // 2
