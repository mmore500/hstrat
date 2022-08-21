import math


def calc_provided_resolution(
    size_curb: int,
    num_stratum_depositions_completed: int,
) -> int:
    """After n strata have been deposited, what resolution is provided?

    Resolution may be negative, indicating that geom seq nth root should be
    used.
    """
    # (resolution + 1) * log2(num_stratum_depositions_completed) <= size_curb
    # (resolution + 1) * ceil(log2(num_depisitons)) == size_curb
    # resolution + 1 == size_curb / ceil(log2(num_depisitons))
    # resolution = size_curb / ceil(log2(num_depisitons)) - 1
    res = (
        int(
            math.floor(
                size_curb
                # int cast allows for other integer-like types i.e., np int64 etc
                / (
                    int(num_stratum_depositions_completed).bit_length() + 1
                )  # - 1?
            )
        )
        - 2
    )  # - 1 ?
    return res
