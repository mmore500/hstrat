"""Provides numba integr array types, or null fallback.

Type must be declared outside jit'ed function or numba fails.
"""


from ._is_in_coverage_run import is_in_coverage_run

try:
    import numba as nb
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    jit_numba_int8_arr_t = None
    jit_numba_int16_arr_t = None
    jit_numba_int32_arr_t = None
    jit_numba_int64_arr_t = None
    jit_numba_uint8_arr_t = None
    jit_numba_uint16_arr_t = None
    jit_numba_uint32_arr_t = None
    jit_numba_uint64_arr_t = None
else:
    if is_in_coverage_run():
        # when numba disabled for coverage testing,
        # using nb.types.int64_ causes numpy TypeError
        jit_numba_int8_arr_t = None
        jit_numba_int16_arr_t = None
        jit_numba_int32_arr_t = None
        jit_numba_int64_arr_t = None
        jit_numba_uint8_arr_t = None
        jit_numba_uint16_arr_t = None
        jit_numba_uint32_arr_t = None
        jit_numba_uint64_arr_t = None
    else:  # pragma: no cover
        # exclude from coverage because jit compilation disabled in cov runs
        jit_numba_int8_arr_t = nb.types.int8[:]
        jit_numba_int16_arr_t = nb.types.int16[:]
        jit_numba_int32_arr_t = nb.types.int32[:]
        jit_numba_int64_arr_t = nb.types.int64[:]
        jit_numba_uint8_arr_t = nb.types.uint8[:]
        jit_numba_uint16_arr_t = nb.types.uint16[:]
        jit_numba_uint32_arr_t = nb.types.uint32[:]
        jit_numba_uint64_arr_t = nb.types.uint64[:]
