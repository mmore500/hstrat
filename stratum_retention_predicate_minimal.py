def stratum_retention_predicate_minimal(
    # *,
    stratum_rank: int,
    column_layers_deposited: int,
) -> bool:
    return stratum_rank in (0, column_layers_deposited - 1,)
