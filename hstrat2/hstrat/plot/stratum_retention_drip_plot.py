import opytional as opyt
from matplotlib import pyplot as plt
import typing

from ..HereditaryStratigraphicColumn import HereditaryStratigraphicColumn

def stratum_retention_drip_plot(
    stratum_retention_policy: typing.Any,
    num_generations: int,
    do_show: bool=True,
    axes: typing.Optional[plt.matplotlib.axes.Axes]=None,
) -> plt.matplotlib.axes.Axes:
    """Plot position of retained strata within a hereditary stratigraphic
    column over successive depositions under a particular stratum retention
    policy.

    Parameters
    ----------
    stratum_retention_policy: any
        Object specifying stratum retention policy.
    num_generations: int
        Number of generations to plot.
    axes : matplotlib/pylab axes, optional
        If a valid matplotlib.axes.Axes instance, the phylogram is plotted
        in that Axes. By default (None), a new figure is created.
    do_show : bool, optional
        Whether to show() the plot automatically.
     """

    if axes is None:
        fig = plt.figure()
        axes = fig.add_subplot(1, 1, 1)
    elif not isinstance(axes, plt.matplotlib.axes.Axes):
        raise ValueError(f"Invalid argument for axes: {axes}")

    column = HereditaryStratigraphicColumn(
        stratum_retention_policy=stratum_retention_policy,
    )
    for gen in range(1, num_generations):
        for rank in stratum_retention_policy.GenDropRanks(
            gen,
            opyt.apply_if_or_value(
                stratum_retention_policy.IterRetainedRanks,
                lambda x: x(gen),
                column.IterRetainedRanks(),
            ),
        ):
            axes.plot([rank, rank], [rank, gen], 'k')
        column.DepositStratum()

    for remaining_rank in opyt.apply_if_or_value(
        stratum_retention_policy.IterRetainedRanks,
        lambda x: x(gen),
        column.IterRetainedRanks(),
    ):
        axes.plot([remaining_rank, remaining_rank], [remaining_rank, gen], 'k')


    axes.invert_yaxis()

    axes.set_xlabel('Position (Rank)')
    axes.set_ylabel('Generation')

    if do_show: plt.show()

    return axes
