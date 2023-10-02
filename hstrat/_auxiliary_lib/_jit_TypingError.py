"""Provides numba TypingError exeption or tuple as exception nop.

Type must be declared outside jit'ed function or numba fails.
"""

from ._is_in_coverage_run import is_in_coverage_run

try:
    import numba as nb
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    jit_TypingError = tuple()  # empty tuple is nop in except clause
else:
    if is_in_coverage_run():
        # when numba disabled for coverage testing,
        jit_TypingError = tuple()  # empty tuple is nop in except clause
    else:  # pragma: no cover
        # exclude from coverage because jit compilation disabled in cov runs
        jit_TypingError = nb.TypingError
