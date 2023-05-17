def calc_geom_seq_nth_root_transition_rank(size_curb: int) -> int:
    """Rank where gsnra first appears. Rank before is last before gsnra."""
    res = 2 ** (size_curb - 1)
    return res
