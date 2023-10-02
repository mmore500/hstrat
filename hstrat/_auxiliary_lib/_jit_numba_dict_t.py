"""Provides numba dict type or builtin bool type.

Type must be declared outside jit'ed function or numba fails.
"""

import typing

from ._is_in_coverage_run import is_in_coverage_run


class _shim:
    def empty(self: "_shim", *args, **kwargs) -> typing.Dict:
        return dict()


try:
    from numba.typed import Dict
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    jit_numba_dict_t = _shim()
else:
    if is_in_coverage_run():
        jit_numba_dict_t = _shim()
    else:  # pragma: no cover
        # exclude from coverage because jit compilation disabled in cov runs
        jit_numba_dict_t = Dict
