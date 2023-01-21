from ._AnyTreeAscendingIter import AnyTreeAscendingIter
from ._RecursionLimit import RecursionLimit
from ._ScalarFormatterFixedPrecision import ScalarFormatterFixedPrecision
from ._all_same import all_same
from ._apply_swaps import apply_swaps
from ._bit_ceil import bit_ceil
from ._bit_floor import bit_floor
from ._caretdown_marker import caretdown_marker
from ._caretup_marker import caretup_marker
from ._check_testing_requirements import check_testing_requirements
from ._consume import consume
from ._count_unique import count_unique
from ._div_range import div_range
from ._find_bounds import find_bounds
from ._get_hstrat_version import get_hstrat_version
from ._indices_of_unique import indices_of_unique
from ._is_base64 import is_base64
from ._is_in_coverage_run import is_in_coverage_run
from ._is_in_unit_test import is_in_unit_test
from ._is_nondecreasing import is_nondecreasing
from ._is_nonincreasing import is_nonincreasing
from ._is_strictly_decreasing import is_strictly_decreasing
from ._is_strictly_increasing import is_strictly_increasing
from ._iter_chunks import iter_chunks
from ._jit_if_has_numba import jit_if_has_numba
from ._launder_impl_modules import launder_impl_modules
from ._log_once_in_a_row import log_once_in_a_row
from ._memoize_generator import memoize_generator
from ._numba_bool_or_fallback import numba_bool_or_fallback
from ._omit_last import omit_last
from ._pairwise import pairwise
from ._popcount import popcount
from ._release_cur_mpl_fig import release_cur_mpl_fig
from ._scale_luminosity import scale_luminosity
from ._splicewhile import splicewhile
from ._zip_strict import zip_strict

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "all_same",
    "apply_swaps",
    "AnyTreeAscendingIter",
    "bit_ceil",
    "bit_floor",
    "caretdown_marker",
    "caretup_marker",
    "check_testing_requirements",
    "consume",
    "count_unique",
    "div_range",
    "find_bounds",
    "get_hstrat_version",
    "indices_of_unique",
    "is_base64",
    "is_nondecreasing",
    "is_nonincreasing",
    "is_strictly_decreasing",
    "is_strictly_increasing",
    "iter_chunks",
    "jit_if_has_numba",
    "launder_impl_modules",
    "log_once_in_a_row",
    "memoize_generator",
    "numba_bool_or_fallback",
    "omit_last",
    "pairwise",
    "popcount",
    "RecursionLimit",
    "release_cur_mpl_fig",
    "scale_luminosity",
    "ScalarFormatterFixedPrecision",
    "splicewhile",
    "zip_strict",
]

for o in __all__:
    try:
        eval(o).__module__ = __name__
    except (AttributeError, TypeError):
        pass
