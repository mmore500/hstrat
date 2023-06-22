from ._ftor_shim import ftor_shim


def iter_no_calcrank_ftor_shims(member_selector, policy_impls):
    for policy_impl in policy_impls:
        impl_without = lambda *args, **kwargs: policy_impl(
            *args, **kwargs
        ).WithoutCalcRankAtColumnIndex()
        yield ftor_shim(member_selector, impl_without)
