def ftor_shim(member_selector, policy_factory):
    def ctor_shim(spec):
        policy = policy_factory(policy_spec=spec)

        # discard first argument, which is policy
        def call_shim(__, *args, **kwargs):
            return member_selector(policy)(*args, **kwargs)

        return call_shim

    return ctor_shim
