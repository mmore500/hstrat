import typing


def policy_from_record(policy_record: str) -> typing.Any:
    """Parse a policy record string and return the corresponding policy object."""
    from ...stratum_retention_strategy import (  # noqa
        stratum_retention_algorithms as hstrat,
    )

    _ = hstrat  # mark as used to prevent autoflake purge
    return eval(policy_record)  # noqa
