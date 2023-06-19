import typing

import matplotlib as mpl
from matplotlib import pyplot as plt
import seaborn as sns

from ...genome_instrumentation._HereditaryStratigraphicColumn import (
    HereditaryStratigraphicColumn,
)


def strata_retained_frac_lineplot(
    stratum_retention_policy: typing.Any,
    num_generations: int,
    do_show: bool = False,
    ax: typing.Optional[plt.matplotlib.axes.Axes] = None,
) -> plt.matplotlib.axes.Axes:
    """Plot fraction deposited strata that are retained at each generation.

    Parameters
    ----------
    stratum_retention_policy : any
        Object specifying stratum retention policy.
    num_generations : int
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

    xs = [0]
    ys = [1]
    column = HereditaryStratigraphicColumn(
        stratum_retention_policy=stratum_retention_policy,
    )
    for gen in range(1, num_generations):
        xs.append(gen)
        if stratum_retention_policy.CalcNumStrataRetainedExact is not None:
            ys.append(
                stratum_retention_policy.CalcNumStrataRetainedExact(gen) / gen,
            )
        else:
            ys.append(column.GetNumStrataRetained() / gen)
            column.DepositStratum()

    sns.lineplot(
        x=xs,
        y=ys,
        ax=ax,
    )
    ax.set_xlabel("Generation")
    ax.set_ylabel("Frac Strata Retained")

    ax.xaxis.set_major_locator(
        mpl.ticker.MaxNLocator(
            nbins="auto",
            steps=[1, 2, 5, 10],
            integer=True,
            min_n_ticks=0,
        )
    )
    ax.set_ylim([-0.05, 1.05])

    # strip any negative xticks
    ax.set_xticks([tick for tick in ax.get_xticks() if tick >= 0])

    if do_show:
        plt.show()

    return ax
