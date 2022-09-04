import mmh3


def decide_if_discard(
    hash_salt: int,
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
            hash_salt,
        )
        % 2
    )
