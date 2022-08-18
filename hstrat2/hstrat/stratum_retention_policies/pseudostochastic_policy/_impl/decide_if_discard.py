import mmh3


def decide_if_discard(
    random_seed: int,
    stratum_rank: int,
    num_stratum_depositions_completed: int,
) -> bool:
    return (
        mmh3.hash(
            str(
                (
                    stratum_rank,
                    num_stratum_depositions_completed,
                )
            ),
            random_seed,
        )
        % 2
    )
