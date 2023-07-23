import typing

from .._auxiliary_lib import get_hstrat_version


def policy_to_records(policy: typing.Callable) -> typing.Dict:
    """Serialize a stratum retention policy to a dict composed of builtin
    types."""

    spec = policy.GetSpec()
    return {
        "policy_algo": spec.GetAlgoIdentifier(),
        "policy_spec": {
            k.lstrip("_"): v  # strip leading underscores on private members
            for k, v in spec.__dict__.items()
        },
        "policy": policy.GetEvalCtor(),
        "hstrat_version": get_hstrat_version(),
    }
