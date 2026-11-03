import types
import typing

from downstream import dstream


def resolve_dstream_algo(
    dstream_algo: typing.Union[str, types.ModuleType],
) -> types.ModuleType:
    """Look up downstream algorithm module by name (e.g.,
    "dstream.steady_algo"), if not already a module.

    Names are evaluated with `dstream` available, as elsewhere in hstrat
    and downstream (e.g., downstream's `explode_lookup_unpacked`).
    """
    if isinstance(dstream_algo, str):
        return eval(dstream_algo, {"dstream": dstream})  # nosec B307
    return dstream_algo
