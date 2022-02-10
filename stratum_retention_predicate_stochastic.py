import random

def stratum_retention_predicate_stochastic(
    stratum_rank: int,
    column_layers_deposited: int,
) -> bool:
    if stratum_rank and stratum_rank == column_layers_deposited - 2:
        return random.choice([True, False])
    else: return True
