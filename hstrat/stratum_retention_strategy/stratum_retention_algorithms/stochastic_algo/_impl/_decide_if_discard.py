import random


def decide_if_discard(
    stratum_rank: int,
    num_stratum_depositions_completed: int,
) -> bool:
    return random.choice([True, False])
