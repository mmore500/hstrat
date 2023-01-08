import random


def decide_if_discard(
    stratum_rank: int,
    num_stratum_depositions_completed: int,
    retention_probability: float,
) -> bool:
    return not (random.random() < retention_probability)
