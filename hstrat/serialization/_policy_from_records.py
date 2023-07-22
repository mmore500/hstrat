import typing

from .._auxiliary_lib import get_hstrat_version, log_once_in_a_row
from ._impl import policy_from_record
from ._policy_to_records import policy_to_records


def policy_from_records(records: typing.Dict) -> typing.Callable:
    """Deserialize a stratum retention policy from a dict composed of builtin
    data types.
    """
    if get_hstrat_version() != records["hstrat_version"]:
        log_once_in_a_row(
            f"""policy_from_records version mismatch, record is version {
                records['hstrat_version']
            } and software is version {
                get_hstrat_version()
            }"""
        )
        # return policy without any further safety checks
        return policy_from_record(records["policy"])

    deserialized_policy = policy_from_record(records["policy"])

    # safety check metadata
    deserialized_policy_records = policy_to_records(deserialized_policy)
    if not all(
        k not in records or v == records[k]
        for k, v in deserialized_policy_records.items()
    ):
        log_once_in_a_row(
            f"""policy_from_records metadata mismatch, records are {
                records
            } and records from deserialized policy are {
                deserialized_policy_records
            }"""
        )

    return deserialized_policy
