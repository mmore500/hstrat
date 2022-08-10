from matplotlib import pyplot as plt
import typing

from .mrca_uncertainty_absolute_plot import mrca_uncertainty_absolute_plot
from .mrca_uncertainty_relative_plot import mrca_uncertainty_relative_plot
from .strata_retained_frac_plot import strata_retained_frac_plot
from .strata_retained_num_plot import strata_retained_num_plot
from .stratum_retention_drip_plot import stratum_retention_drip_plot

def policy_panel_plot(
    stratum_retention_policy: typing.Any,
    num_generations: int,
    do_show: bool=True,
) -> plt.matplotlib.figure.Figure:
    """Draw multipanel figure to holisticaly describe stratum retention policy
    at a particular generation.

    Parameters
    ----------
    stratum_retention_policy: any
        Object specifying stratum retention policy.
    num_generations: int
        Number of generations to plot.
    do_show : bool, optional
        Whether to show() the plot automatically.
     """

    fig, (
        (top_left_ax, top_right_ax),
        (mid_left_ax, mid_right_ax),
        (bot_left_ax, bot_right_ax),
    ) = plt.subplots(3, 2)
    fig.suptitle(str(stratum_retention_policy))

    # left column
    stratum_retention_drip_plot(
        stratum_retention_policy=stratum_retention_policy,
        num_generations=num_generations,
        axes=top_left_ax,
        do_show=False,
    )
    mrca_uncertainty_absolute_plot(
        stratum_retention_policy=stratum_retention_policy,
        num_generations=num_generations,
        axes=mid_left_ax,
        do_show=False,
    )
    mrca_uncertainty_relative_plot(
        stratum_retention_policy=stratum_retention_policy,
        num_generations=num_generations,
        axes=bot_left_ax,
        do_show=False,
    )

    # right column
    strata_retained_num_plot(
        stratum_retention_policy=stratum_retention_policy,
        num_generations=num_generations,
        axes=top_right_ax,
        do_show=False,
    )

    strata_retained_frac_plot(
        stratum_retention_policy=stratum_retention_policy,
        num_generations=num_generations,
        axes=mid_right_ax,
        do_show=False,
    )

    #TODO bot_right_ax text panel with params etc

    if do_show: plt.show()

    return fig
