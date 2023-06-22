from ._ftor_shim import ftor_shim


def iter_ftor_shims(member_selector, policy_impls):
    for policy_impl in policy_impls:
        yield ftor_shim(member_selector, policy_impl)
