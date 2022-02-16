from .StratumRetentionPredicateDepthProportionalResolution \
    import StratumRetentionPredicateDepthProportionalResolution
from .StratumRetentionPredicateMaximal import StratumRetentionPredicateMaximal
from .StratumRetentionPredicateMinimal import StratumRetentionPredicateMinimal
from .StratumRetentionPredicateFixedResolution \
    import StratumRetentionPredicateFixedResolution
from .StratumRetentionPredicateRecencyProportionalResolution \
    import StratumRetentionPredicateRecencyProportionalResolution
from .StratumRetentionPredicateRecursiveInterspersion \
    import StratumRetentionPredicateRecursiveInterspersion
from .StratumRetentionPredicateStochastic \
    import StratumRetentionPredicateStochastic

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    'StratumRetentionPredicateDepthProportionalResolution',
    'StratumRetentionPredicateFixedResolution',
    'StratumRetentionPredicateMaximal',
    'StratumRetentionPredicateMinimal',
    'StratumRetentionPredicateRecencyProportionalResolution',
    'StratumRetentionPredicateRecursiveInterspersion',
    'StratumRetentionPredicateStochastic',
]
