import itertools as it
import typing

import matplotlib as mpl
from matplotlib import pyplot as plt

from ...genome_instrumentation._HereditaryStratigraphicColumn import (
    HereditaryStratigraphicColumn,
)


def mrca_uncertainty_relative_barplot(
    stratum_retention_policy: typing.Any,
    num_generations: int,
    do_show: bool = False,
    ax: typing.Optional[plt.matplotlib.axes.Axes] = None,
) -> plt.matplotlib.axes.Axes:
    """Profile distribution of retained rank spacing under a retention policy.

    Plots relative uncertainty for MRCA estimation over column ranks
    (positions) in a hereditary stratigraphic column at a particular generation
    under a particular stratum retention policy.

    Parameters
    ----------
    stratum_retention_policy : Callable
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
    ys = [0]
    column = HereditaryStratigraphicColumn(
        stratum_retention_policy=stratum_retention_policy,
    )
    for gen in range(1, num_generations):
        xs.append(gen)
        if stratum_retention_policy.CalcNumStrataRetainedExact is not None:
            ys.append(
                stratum_retention_policy.CalcMrcaUncertaintyAbsExact(
                    num_generations,
                    num_generations,
                    gen,
                )
                / (num_generations - gen),
            )
        else:
            ys.append(column.GetNumStrataRetained())
            column.DepositStratum()

    ax.bar(
        xs,
        ys,
        color=[
            *it.islice(
                it.cycle(
                    [
                        "mediumpurple",
                        "mediumslateblue",
                    ]
                ),
                num_generations,
            )
        ],
        width=1.0,
    )
    ax.set_xlabel("Position (Rank)")
    ax.set_ylabel("Relative MRCA\n Uncertainty", labelpad=20)
    ax.xaxis.set_major_locator(
        mpl.ticker.MaxNLocator(
            nbins="auto",
            steps=[1, 2, 5, 10],
            integer=True,
            min_n_ticks=0,
        )
    )
    ax.yaxis.set_major_locator(
        mpl.ticker.MaxNLocator(
            nbins="auto",
            steps=[1, 2, 5, 10],
            min_n_ticks=0,
        )
    )

    # strip any negative xticks
    ax.set_xticks([tick for tick in ax.get_xticks() if tick >= 0])

    if do_show:
        plt.show()

    return ax
