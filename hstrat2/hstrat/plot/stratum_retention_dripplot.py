import opytional as opyt
from matplotlib import pyplot as plt
from matplotlib import ticker
import typing

from ...helpers import caretdown_marker

from ..HereditaryStratigraphicColumn import HereditaryStratigraphicColumn

def stratum_retention_dripplot(
    stratum_retention_policy: typing.Any,
    num_generations: int,
    do_show: bool=True,
    ax: typing.Optional[plt.matplotlib.axes.Axes]=None,
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
    ax : matplotlib/pylab axes, optional
        If a valid matplotlib.axes.Axes instance, the plot is drawn in that
        Axes. By default (None), a new axes is created.
    do_show : bool, optional
        Whether to show() the plot automatically.
     """

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
    elif not isinstance(ax, plt.matplotlib.axes.Axes):
        raise ValueError(f"Invalid argument for ax: {ax}")

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
            ax.plot([rank, rank], [rank, gen], 'k')
            ax.plot(
                rank,
                gen,
                ms=min(200 / num_generations, 20),
                marker=caretdown_marker,
                markerfacecolor='None',
                markeredgecolor='r',
                markeredgewidth=1,
            )
        column.DepositStratum()

    for remaining_rank in opyt.apply_if_or_value(
        stratum_retention_policy.IterRetainedRanks,
        lambda x: x(num_generations),
        column.IterRetainedRanks(),
    ):
        ax.plot(
            [remaining_rank, remaining_rank],
            [remaining_rank, num_generations - 1],
            'k',
        )
        ax.plot(
            remaining_rank,
            num_generations - 1,
            ms=min(200 / num_generations, 20),
            marker=caretdown_marker,
            markerfacecolor='k',
            markeredgecolor='k',
            markeredgewidth=1,
        )

    # make space for triangle markers
    ymin, ymax = ax.get_ylim()
    ax.set_ylim([ymin, ymax + 2])
    ax.xaxis.set_major_locator(ticker.MaxNLocator(
        nbins='auto',
        steps=[1, 2, 5, 10],
        integer=True,
        min_n_ticks=0,
    ))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(
        nbins='auto',
        steps=[1, 2, 5, 10],
        integer=True,
        min_n_ticks=0,
    ))

    ax.set_xlabel('Position (Rank)')
    ax.set_ylabel('Generation')

    if do_show: plt.show()

    return ax
