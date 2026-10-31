from ..._auxiliary_lib import get_package_name, load_cppimportable_module

_impl_mod = load_cppimportable_module(
    "_origin_time_cpp_impl", get_package_name(__name__)
)
brute_upgma = _impl_mod.brute_upgma
cross_pair_sums = _impl_mod.cross_pair_sums
pair_estimate = _impl_mod.pair_estimate
pool_inversions = _impl_mod.pool_inversions
scaffold_upgma = _impl_mod.scaffold_upgma
