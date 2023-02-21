import typing


def policy_from_record(policy_record: str) -> typing.Any:
    """Parse a policy record string and return the corresponding policy object."""
    # noqa
    from ...stratum_retention_strategy import (
        stratum_retention_algorithms as hstrat,
    )

    return eval(policy_record)  # noqa
