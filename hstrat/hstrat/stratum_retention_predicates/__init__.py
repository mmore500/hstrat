"""Functors that implement stratum retention policies by specifying
whether a stratum with deposition rank r should be retained within
a hereditary stratigraphic column after n strata have been
deposited."""


from .StratumRetentionPredicateDepthProportionalResolution \
    import StratumRetentionPredicateDepthProportionalResolution
from .StratumRetentionPredicateNominalResolution import StratumRetentionPredicateNominalResolution
from .StratumRetentionPredicatePerfectResolution import StratumRetentionPredicatePerfectResolution
from .StratumRetentionPredicateFixedResolution \
    import StratumRetentionPredicateFixedResolution
from .StratumRetentionPredicateRecencyProportionalResolution \
    import StratumRetentionPredicateRecencyProportionalResolution
from .StratumRetentionPredicateStochastic \
    import StratumRetentionPredicateStochastic

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    'StratumRetentionPredicateDepthProportionalResolution',
    'StratumRetentionPredicateFixedResolution',
    'StratumRetentionPredicatePerfectResolution',
    'StratumRetentionPredicateNominalResolution',
    'StratumRetentionPredicateRecencyProportionalResolution',
    'StratumRetentionPredicateStochastic',
]
