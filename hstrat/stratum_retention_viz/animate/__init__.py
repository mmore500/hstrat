"""Animations for stratum retention policies."""

from ._policy_panel_animate import policy_panel_animate
from ._stratum_retention_animate import stratum_retention_animate

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "policy_panel_animate",
    "stratum_retention_animate",
]

from ..._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
