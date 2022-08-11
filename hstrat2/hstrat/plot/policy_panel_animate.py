import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.animation
import typing

from .policy_panel_plot import policy_panel_plot

def policy_panel_animate(
    stratum_retention_policy: typing.Any,
    num_generations: int,
    do_show: bool=True,

) -> None:
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

    fig = plt.figure(figsize=(8, 6), dpi=80)

    def update_func(frame) -> None:
        for ax in fig.axes:
            fig.delaxes(ax)
        fig.clear()
        policy_panel_plot(
            stratum_retention_policy=stratum_retention_policy,
            num_generations=frame,
            do_show=False,
            fig=fig,
        )

    res = mpl.animation.FuncAnimation(
        fig,
        update_func,
        frames=range(num_generations),
        interval=500,
        blit=False,
    )

    if do_show: plt.show()

    return res
