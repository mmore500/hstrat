from matplotlib import pyplot as plt
import typing

from .mrca_uncertainty_absolute_barplot import mrca_uncertainty_absolute_barplot
from .mrca_uncertainty_relative_barplot import mrca_uncertainty_relative_barplot
from .strata_retained_frac_lineplot import strata_retained_frac_lineplot
from .strata_retained_num_lineplot import strata_retained_num_lineplot
from .stratum_retention_dripplot import stratum_retention_dripplot

def policy_panel_plot(
    stratum_retention_policy: typing.Any,
    num_generations: int,
    do_show: bool=True,
    fig: typing.Optional[plt.matplotlib.figure.Figure]=None,
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
    fig : matplotlib/pylab figure, optional
        If a valid matplotlib.figure.Figure instance, the plot is drawn in that
        Figure. By default (None), a new figure is created.
     """

    if fig is None:
        fig = plt.figure()
    elif not isinstance(fig, plt.matplotlib.figure.Figure):
        raise ValueError(f"Invalid argument for fig: {fig}")

    (
        (top_left_ax, top_right_ax),
        (mid_left_ax, mid_right_ax),
        (bot_left_ax, bot_right_ax),
    ) = fig.subplots(3, 2)
    fig.suptitle(str(stratum_retention_policy))

    # left column
    stratum_retention_dripplot(
        stratum_retention_policy=stratum_retention_policy,
        num_generations=num_generations,
        ax=top_left_ax,
        do_show=False,
    )
    mrca_uncertainty_absolute_barplot(
        stratum_retention_policy=stratum_retention_policy,
        num_generations=num_generations,
        ax=mid_left_ax,
        do_show=False,
    )
    mrca_uncertainty_relative_barplot(
        stratum_retention_policy=stratum_retention_policy,
        num_generations=num_generations,
        ax=bot_left_ax,
        do_show=False,
    )

    # right column
    strata_retained_num_lineplot(
        stratum_retention_policy=stratum_retention_policy,
        num_generations=num_generations,
        ax=top_right_ax,
        do_show=False,
    )

    strata_retained_frac_lineplot(
        stratum_retention_policy=stratum_retention_policy,
        num_generations=num_generations,
        ax=mid_right_ax,
        do_show=False,
    )

    #TODO bot_right_ax text panel with params etc

    if do_show: plt.show()

    return fig
