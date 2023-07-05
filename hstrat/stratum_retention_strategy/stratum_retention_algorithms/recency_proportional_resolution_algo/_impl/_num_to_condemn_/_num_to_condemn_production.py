from ......_auxiliary_lib import count_trailing_zeros


def num_to_condemn_production(
    recency_proportional_resolution: int,
    num_stratum_depositions_completed: int,
) -> int:
    """How many strata should be eliminated after
    num_stratum_depositions_completed have been deposited and the
    num_stratum_depositions_completed + 1'th deposition is in progress?

    Inscrutable bit magic translation of num_to_condemn_reference.
    """
    # protect against stray numpy integer types
    recency_proportional_resolution = int(recency_proportional_resolution)
    num_stratum_depositions_completed = int(num_stratum_depositions_completed)

    comparison_value = 2 * (recency_proportional_resolution + 1)
    binary_magnitude_diff = max(
        num_stratum_depositions_completed.bit_length()
        - comparison_value.bit_length(),
        0,
    )
    comparison_value <<= binary_magnitude_diff

    # did we shift enough to equalize magnitude of comparison value?
    assert (
        num_stratum_depositions_completed.bit_length()
        <= comparison_value.bit_length()
    )

    # add one if need to perform one final shift to be bigger
    binary_magnitude_diff += (
        num_stratum_depositions_completed >= comparison_value
    )

    return min(
        count_trailing_zeros(num_stratum_depositions_completed),
        binary_magnitude_diff,
    )
