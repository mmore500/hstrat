"""Provides numba dict type or builtin bool type.

Type must be declared outside jit'ed function or numba fails.
"""

import typing

from ._is_in_coverage_run import is_in_coverage_run


class _shim:
    def empty(*args, **kwargs) -> typing.Type:
        return dict()


try:
    from numba.typed import Dict
except ImportError:
    jit_numba_dict_t = shim_
else:
    if is_in_coverage_run():
        jit_numba_dict_t = shim_
    else:
        jit_numba_dict_t = Dict