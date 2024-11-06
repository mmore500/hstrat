"""Tools to specify stratum retention policy."""

from hstrat._auxiliary_lib import lazy_attach

from . import (
    stratum_retention_algorithms,
    stratum_retention_policy_evaluators,
    stratum_retention_policy_parameterizers,
)

__getattr__, __dir__, __all__ = lazy_attach(
    __name__,
    submodules=[
        "stratum_retention_algorithms",
        "stratum_retention_policy_evaluators",
        "stratum_retention_policy_parameterizers",
    ],
    submod_attrs={
        "stratum_retention_algorithms": stratum_retention_algorithms.__all__,
        "stratum_retention_policy_parameterizers": stratum_retention_policy_parameterizers.__all__,
        "stratum_retention_policy_evaluators": stratum_retention_policy_evaluators.__all__,
    },
    should_launder=[].__contains__,
)
del lazy_attach
