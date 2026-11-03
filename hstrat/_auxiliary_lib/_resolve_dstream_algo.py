import types
import typing

from downstream import dstream


def resolve_dstream_algo(
    dstream_algo: typing.Union[str, types.ModuleType],
) -> types.ModuleType:
    """Look up downstream algorithm module by name (e.g.,
    "dstream.steady_algo" or "steady_algo"), if not already a module."""
    if isinstance(dstream_algo, str):
        return getattr(dstream, dstream_algo.removeprefix("dstream."))
    return dstream_algo
