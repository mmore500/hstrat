from ._AnyTreeAscendingIter import AnyTreeAscendingIter
from ._AnyTreeFastLeafIter import AnyTreeFastLeafIter
from ._AnyTreeFastLevelOrderIter import AnyTreeFastLevelOrderIter
from ._AnyTreeFastPostOrderIter import AnyTreeFastPostOrderIter
from ._AnyTreeFastPreOrderIter import AnyTreeFastPreOrderIter
from ._BioPhyloTree import BioPhyloTree
from ._CopyableSeriesItemsIter import CopyableSeriesItemsIter
from ._HereditaryStratigraphicArtifact import HereditaryStratigraphicArtifact
from ._RecursionLimit import RecursionLimit
from ._RngStateContext import RngStateContext
from ._ScalarFormatterFixedPrecision import ScalarFormatterFixedPrecision
from ._alifestd_aggregate_phylogenies import alifestd_aggregate_phylogenies
from ._alifestd_assign_contiguous_ids import alifestd_assign_contiguous_ids
from ._alifestd_assign_root_ancestor_token import (
    alifestd_assign_root_ancestor_token,
)
from ._alifestd_collapse_unifurcations import alifestd_collapse_unifurcations
from ._alifestd_convert_root_ancestor_token import (
    alifestd_convert_root_ancestor_token,
)
from ._alifestd_find_chronological_inconsistency import (
    alifestd_find_chronological_inconsistency,
)
from ._alifestd_find_leaf_ids import alifestd_find_leaf_ids
from ._alifestd_find_root_ids import alifestd_find_root_ids
from ._alifestd_has_compact_ids import alifestd_has_compact_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_has_multiple_roots import alifestd_has_multiple_roots
from ._alifestd_is_asexual import alifestd_is_asexual
from ._alifestd_is_chronologically_ordered import (
    alifestd_is_chronologically_ordered,
)
from ._alifestd_is_sexual import alifestd_is_sexual
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_make_ancestor_id_col import alifestd_make_ancestor_id_col
from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_make_empty import alifestd_make_empty
from ._alifestd_parse_ancestor_id import alifestd_parse_ancestor_id
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_reroot_at_id_asexual import alifestd_reroot_at_id_asexual
from ._alifestd_splay_polytomies import alifestd_splay_polytomies
from ._alifestd_to_working_format import alifestd_to_working_format
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._alifestd_unfurl_lineage_asexual import alifestd_unfurl_lineage_asexual
from ._alifestd_validate import alifestd_validate
from ._all_same import all_same
from ._all_unique import all_unique
from ._anynode_deepcopy_except_neighbors import (
    anynode_deepcopy_except_neighbors,
)
from ._anytree_calc_leaf_counts import anytree_calc_leaf_counts
from ._anytree_cardinality import anytree_cardinality
from ._anytree_has_grandparent import anytree_has_grandparent
from ._anytree_has_sibling import anytree_has_sibling
from ._anytree_iterative_deepcopy import anytree_iterative_deepcopy
from ._anytree_peel_sibling_to_cousin import anytree_peel_sibling_to_cousin
from ._anytree_tree_to_alife_dataframe import anytree_tree_to_alife_dataframe
from ._apply_swaps import apply_swaps
from ._argsort import argsort
from ._as_compact_type import as_compact_type
from ._as_nullable_type import as_nullable_type
from ._assign_intersecting_subsets import assign_intersecting_subsets
from ._bit_ceil import bit_ceil
from ._bit_floor import bit_floor
from ._capitalize_n import capitalize_n
from ._caretdown_marker import caretdown_marker
from ._caretup_marker import caretup_marker
from ._check_testing_requirements import check_testing_requirements
from ._cmp import cmp
from ._cmp_approx import cmp_approx
from ._consume import consume
from ._coshuffled import coshuffled
from ._count_trailing_ones import count_trailing_ones
from ._count_trailing_zeros import count_trailing_zeros
from ._count_unique import count_unique
from ._curried_binary_search_jit import curried_binary_search_jit
from ._deep_listify import deep_listify
from ._demark import demark
from ._div_range import div_range
from ._find_bounds import find_bounds
from ._flag_last import flag_last
from ._flat_len import flat_len
from ._generate_n import generate_n
from ._generate_omission_subsets import generate_omission_subsets
from ._get_hstrat_version import get_hstrat_version
from ._get_nullable_mask import get_nullable_mask
from ._get_nullable_vals import get_nullable_vals
from ._give_len import give_len
from ._indices_of_unique import indices_of_unique
from ._intersect_ranges import intersect_ranges
from ._is_base64 import is_base64
from ._is_in import is_in
from ._is_in_coverage_run import is_in_coverage_run
from ._is_in_unit_test import is_in_unit_test
from ._is_nondecreasing import is_nondecreasing
from ._is_nonincreasing import is_nonincreasing
from ._is_strictly_decreasing import is_strictly_decreasing
from ._is_strictly_increasing import is_strictly_increasing
from ._is_subset import is_subset
from ._iter_chunks import iter_chunks
from ._iter_monotonic_equivalencies import iter_monotonic_equivalencies
from ._iter_monotonic_equivalencies_reverse import (
    iter_monotonic_equivalencies_reverse,
)
from ._iter_slices import iter_slices
from ._jit import jit
from ._jit_numba_dict_t import jit_numba_dict_t
from ._jit_numba_integer_array_ts import (
    jit_numba_int8_arr_t,
    jit_numba_int16_arr_t,
    jit_numba_int32_arr_t,
    jit_numba_int64_arr_t,
    jit_numba_uint8_arr_t,
    jit_numba_uint16_arr_t,
    jit_numba_uint32_arr_t,
    jit_numba_uint64_arr_t,
)
from ._jit_numpy_bool_t import jit_numpy_bool_t
from ._jit_numpy_int64_t import jit_numpy_int64_t
from ._launder_impl_modules import launder_impl_modules
from ._log_once_in_a_row import log_once_in_a_row
from ._make_intersecting_subsets import make_intersecting_subsets
from ._memoize_generator import memoize_generator
from ._min_array_dtype import min_array_dtype
from ._numpy_fromiter_polyfill import numpy_fromiter_polyfill
from ._numpy_index import numpy_index
from ._numpy_index_flat import numpy_index_flat
from ._omit_last import omit_last
from ._pairwise import pairwise
from ._parse_from_numeral_system import parse_from_numeral_system
from ._popcount import popcount
from ._raises import raises
from ._random_choice_generator import random_choice_generator
from ._release_cur_mpl_fig import release_cur_mpl_fig
from ._render_to_base64url import render_to_base64url
from ._render_to_numeral_system import render_to_numeral_system
from ._reversed_enumerate import reversed_enumerate
from ._reversed_range import reversed_range
from ._scale_luminosity import scale_luminosity
from ._seed_random import seed_random
from ._splicewhile import splicewhile
from ._swap_rows_and_indices import swap_rows_and_indices
from ._to_tril import to_tril
from ._unfurl_lineage_with_contiguous_ids import (
    unfurl_lineage_with_contiguous_ids,
)
from ._unpairwise import unpairwise
from ._unzip import unzip
from ._with_omission import with_omission
from ._with_rng_state_context import with_rng_state_context
from ._zip_strict import zip_strict

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "alifestd_aggregate_phylogenies",
    "alifestd_assign_contiguous_ids",
    "alifestd_assign_root_ancestor_token",
    "alifestd_collapse_unifurcations",
    "alifestd_find_chronological_inconsistency",
    "alifestd_find_leaf_ids",
    "alifestd_find_root_ids",
    "alifestd_has_compact_ids",
    "alifestd_has_contiguous_ids",
    "alifestd_has_multiple_roots",
    "alifestd_is_asexual",
    "alifestd_is_chronologically_ordered",
    "alifestd_is_sexual",
    "alifestd_is_topologically_sorted",
    "alifestd_make_ancestor_id_col",
    "alifestd_make_ancestor_list_col",
    "alifestd_make_empty",
    "alifestd_parse_ancestor_id",
    "alifestd_parse_ancestor_ids",
    "alifestd_reroot_at_id_asexual",
    "alifestd_convert_root_ancestor_token",
    "alifestd_splay_polytomies",
    "alifestd_to_working_format",
    "alifestd_topological_sort",
    "alifestd_try_add_ancestor_id_col",
    "alifestd_unfurl_lineage_asexual",
    "alifestd_validate",
    "all_same",
    "all_unique",
    "anynode_deepcopy_except_neighbors",
    "anytree_calc_leaf_counts",
    "anytree_cardinality",
    "anytree_iterative_deepcopy",
    "anytree_has_grandparent",
    "anytree_has_sibling",
    "anytree_peel_sibling_to_cousin",
    "anytree_tree_to_alife_dataframe",
    "apply_swaps",
    "argsort",
    "as_compact_type",
    "as_nullable_type",
    "assign_intersecting_subsets",
    "AnyTreeAscendingIter",
    "AnyTreeFastLeafIter",
    "AnyTreeFastLevelOrderIter",
    "AnyTreeFastPreOrderIter",
    "AnyTreeFastPostOrderIter",
    "BioPhyloTree",
    "bit_ceil",
    "bit_floor",
    "capitalize_n",
    "caretdown_marker",
    "caretup_marker",
    "check_testing_requirements",
    "cmp",
    "cmp_approx",
    "consume",
    "CopyableSeriesItemsIter",
    "count_unique",
    "coshuffled",
    "count_trailing_ones",
    "count_trailing_zeros",
    "curried_binary_search_jit",
    "deep_listify",
    "demark",
    "div_range",
    "find_bounds",
    "flat_len",
    "generate_n",
    "generate_omission_subsets",
    "get_hstrat_version",
    "get_nullable_mask",
    "get_nullable_vals",
    "give_len",
    "flag_last",
    "HereditaryStratigraphicArtifact",
    "indices_of_unique",
    "intersect_ranges",
    "is_base64",
    "is_in",
    "is_in_coverage_run",
    "is_in_unit_test",
    "is_nondecreasing",
    "is_nonincreasing",
    "is_strictly_decreasing",
    "is_strictly_increasing",
    "is_subset",
    "iter_chunks",
    "iter_monotonic_equivalencies",
    "iter_monotonic_equivalencies_reverse",
    "iter_slices",
    "jit",
    "jit_numba_int8_arr_t",
    "jit_numba_int16_arr_t",
    "jit_numba_int32_arr_t",
    "jit_numba_int64_arr_t",
    "jit_numba_uint8_arr_t",
    "jit_numba_uint16_arr_t",
    "jit_numba_uint32_arr_t",
    "jit_numba_uint64_arr_t",
    "jit_numba_dict_t",
    "jit_numpy_bool_t",
    "jit_numpy_int64_t",
    "launder_impl_modules",
    "log_once_in_a_row",
    "make_intersecting_subsets",
    "memoize_generator",
    "min_array_dtype",
    "numpy_fromiter_polyfill",
    "numpy_index",
    "numpy_index_flat",
    "omit_last",
    "pairwise",
    "parse_from_numeral_system",
    "popcount",
    "RecursionLimit",
    "raises",
    "release_cur_mpl_fig",
    "random_choice_generator",
    "render_to_base64url",
    "render_to_numeral_system",
    "reversed_enumerate",
    "reversed_range",
    "RngStateContext",
    "scale_luminosity",
    "ScalarFormatterFixedPrecision",
    "seed_random",
    "splicewhile",
    "swap_rows_and_indices",
    "to_tril",
    "unfurl_lineage_with_contiguous_ids",
    "unpairwise",
    "unzip",
    "with_omission",
    "with_rng_state_context",
    "zip_strict",
]

for o in __all__:
    try:
        eval(o).__module__ = __name__
    except (AttributeError, TypeError):
        pass
