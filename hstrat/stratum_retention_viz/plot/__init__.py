"""Visualizations for stratum retention policies."""

from ._mrca_uncertainty_absolute_barplot import (
    mrca_uncertainty_absolute_barplot,
)
from ._mrca_uncertainty_relative_barplot import (
    mrca_uncertainty_relative_barplot,
)
from ._policy_panel_plot import policy_panel_plot
from ._strata_retained_frac_lineplot import strata_retained_frac_lineplot
from ._strata_retained_num_lineplot import strata_retained_num_lineplot
from ._stratum_retention_dripplot import stratum_retention_dripplot

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "mrca_uncertainty_absolute_barplot",
    "mrca_uncertainty_relative_barplot",
    "policy_panel_plot",
    "strata_retained_frac_lineplot",
    "strata_retained_num_lineplot",
    "stratum_retention_dripplot",
]

from ..._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
