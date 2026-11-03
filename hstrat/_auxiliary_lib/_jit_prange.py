"""Provides numba prange for parallel loops in jit'ed functions, or builtin
range if numba is unavailable."""

try:
    from numba import prange as jit_prange
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    jit_prange = range
