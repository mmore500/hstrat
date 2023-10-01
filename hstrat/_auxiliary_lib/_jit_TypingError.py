"""Provides numba TypingError exeption or tuple as exception nop.

Type must be declared outside jit'ed function or numba fails.
"""

import typing

from ._is_in_coverage_run import is_in_coverage_run


try:
    from numba import TypingError
except (ImportError, ModuleNotFoundError):
    jit_TypingError = TypingError
else:
    if is_in_coverage_run():
        jit_TypingError = tuple()  # empty tuple is nop in except clause
    else:  # pragma: no cover
        jit_TypingError = TypingError
