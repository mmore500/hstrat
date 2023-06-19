import typing

import matplotlib as mpl
from matplotlib import pyplot as plt
import opytional as opyt

from ..._auxiliary_lib import scale_luminosity
from ...genome_instrumentation._HereditaryStratigraphicColumn import (
    HereditaryStratigraphicColumn,
)


def stratum_retention_dripplot(
    stratum_retention_policy: typing.Any,
    num_generations: int,
    do_show: bool = False,
    ax: typing.Optional[plt.matplotlib.axes.Axes] = None,
    draw_extant_history: bool = True,
    draw_extinct_history: bool = True,
    draw_extinct_placeholders: bool = False,
    progress_wrap: typing.Callable = lambda x: x,
) -> plt.matplotlib.axes.Axes:
    """Show history of retained and purged strata at a particular generation.

    Plots position of retained strata within a hereditary stratigraphic
    column over successive depositions under a particular stratum retention
    policy.

    Parameters
    ----------
    stratum_retention_policy : any
        Object specifying stratum retention policy.
    num_generations : int
        Number of generations to plot.
    do_show : bool, optional
        Whether to show() the plot automatically.
    ax : matplotlib/pylab axes, optional
        If a valid matplotlib.axes.Axes instance, the plot is drawn in that
        Axes. By default (None), a new axes is created.
    progress_wrap : Callable, default identity function
        Wrapper applied around generation iterator and row generator for final
        phylogeny compilation process.

        Pass tqdm or equivalent to display progress bars.
    """
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
    elif not isinstance(ax, plt.matplotlib.axes.Axes):
        raise ValueError(f"Invalid argument for ax: {ax}")

    # instantiate column if IterRetainedRanks not available
    column_t = typing.Optional[HereditaryStratigraphicColumn]
    column: column_t = opyt.apply_if_or_else(
        stratum_retention_policy.IterRetainedRanks,
        lambda __: None,
        lambda: HereditaryStratigraphicColumn(
            stratum_retention_policy=stratum_retention_policy,
        ),
    )

    for gen in progress_wrap(range(1, num_generations)):
        for rank in stratum_retention_policy.GenDropRanks(
            gen,
            opyt.apply_if_or_else(
                stratum_retention_policy.IterRetainedRanks,
                lambda x: x(gen),
                lambda: column.IterRetainedRanks(),
            ),
        ):
            if draw_extinct_placeholders:
                ax.plot(
                    rank,
                    num_generations - 1,
                    ms=20 / max(0.2 * num_generations, 1),
                    marker="v",
                    markerfacecolor="None",
                    markeredgecolor="w",
                    markeredgewidth=4 / max(0.2 * num_generations, 1),
                )
                ax.plot(
                    rank,
                    num_generations - 1,
                    ms=max(
                        20 / max(0.2 * num_generations, 1),
                        4,
                    ),
                    marker="v",
                    markerfacecolor=scale_luminosity(
                        "r", max(10 / max(0.2 * num_generations, 1), 1)
                    ),
                    markeredgecolor="r",
                    markeredgewidth=2 / max(0.05 * num_generations, 1),
                )

            if not draw_extinct_history:
                break
            ax.plot(
                rank,
                gen,
                ms=20 / max(0.2 * num_generations, 1),
                marker="v",
                markerfacecolor="None",
                markeredgecolor="w",
                markeredgewidth=4 / max(0.2 * num_generations, 1),
            )
            ax.plot(
                [rank, rank],
                [rank, gen],
                "w",
                lw=4 / max(0.2 * num_generations, 1),
            )
            ax.plot([rank, rank], [rank, gen], "r")
            ax.plot(
                rank,
                gen,
                ms=max(
                    20 / max(0.2 * num_generations, 1),
                    4,
                ),
                marker="v",
                markerfacecolor=scale_luminosity(
                    "r", max(10 / max(0.2 * num_generations, 1), 1)
                ),
                markeredgecolor="r",
                markeredgewidth=2 / max(0.05 * num_generations, 1),
            )
        opyt.apply_if(column, lambda x: x.DepositStratum())

    for remaining_rank in opyt.apply_if_or_else(
        stratum_retention_policy.IterRetainedRanks,
        lambda x: x(num_generations),
        lambda: column.IterRetainedRanks(),
    ):
        ax.plot(
            remaining_rank,
            num_generations - 1,
            ms=20 / max(0.2 * num_generations, 1),
            marker="v",
            markerfacecolor="None",
            markeredgecolor="w",
            markeredgewidth=4 / max(0.2 * num_generations, 1),
        )
        if draw_extant_history:
            ax.plot(
                [remaining_rank, remaining_rank],
                [remaining_rank, num_generations - 1],
                "w",
                lw=4 / max(0.2 * num_generations, 1),
            )
            ax.plot(
                [remaining_rank, remaining_rank],
                [remaining_rank, num_generations - 1],
                "k",
            )
        ax.plot(
            remaining_rank,
            num_generations - 1,
            ms=max(
                20 / max(0.2 * num_generations, 1),
                4,
            ),
            marker="v",
            markerfacecolor="k",
            markeredgecolor="k",
            markeredgewidth=2 / max(0.05 * num_generations, 1),
        )

    # make space for extant underbar
    ymin, ymax = ax.get_ylim()
    ymid = (ymin + ymax) / 2
    ax.set_ylim([min(ymin, ymid - 2), max(ymax, ymid + 2)])
    # make space for triangle markers
    ymin, ymax = ax.get_ylim()
    ax.set_ylim([ymin, ymax + 2])
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
            integer=True,
            min_n_ticks=0,
        )
    )

    # strip any negative xticks
    ax.set_xticks([tick for tick in ax.get_xticks() if tick >= 0])

    # make space for rectangle
    xmin, xmax = ax.get_xlim()
    ax.set_xlim(
        [
            min(xmin, -1),
            max(xmax, num_generations),
        ]
    )
    height = min(3, num_generations)
    ax.add_patch(
        mpl.patches.Rectangle(
            xy=(-0.5, num_generations - 1 - height / 2),
            width=num_generations,
            height=height,
            facecolor=scale_luminosity("C0", 1.5),
            edgecolor=scale_luminosity("C0", 0.5),
            linewidth=6 / max(0.2 * num_generations, 1),
        )
    )

    ax.set_xlabel("Position (Rank)")
    ax.set_ylabel("Retention History\n(Generations)")

    if do_show:
        plt.show()

    return ax
