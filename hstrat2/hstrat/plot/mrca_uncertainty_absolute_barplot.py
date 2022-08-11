import itertools as it
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
import typing
import seaborn as sns

from ..HereditaryStratigraphicColumn import HereditaryStratigraphicColumn

def mrca_uncertainty_absolute_barplot(
    stratum_retention_policy: typing.Any,
    num_generations: int,
    do_show: bool=True,
    ax: typing.Optional[plt.matplotlib.axes.Axes]=None,
) -> plt.matplotlib.axes.Axes:
    """Plot absolute uncertainty for MRCA estimation over column ranks
    (positions) in a hereditary stratigraphic column at a particular generation
    under a particular stratum retention policy.

    Parameters
    ----------
    stratum_retention_policy: Callable
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

    xs = [0]
    ys = [0]
    column = HereditaryStratigraphicColumn(
        stratum_retention_policy=stratum_retention_policy,
    )
    for gen in range(1, num_generations):
        xs.append(gen)
        if stratum_retention_policy.CalcMrcaUncertaintyExact is not None:
            ys.append(stratum_retention_policy.CalcMrcaUncertaintyExact(
                num_generations,
                num_generations,
                gen,
            ))
        else:
            ys.append(float('nan'))

    ax.bar(
        xs,
        ys,
        color=[*it.islice(
            it.cycle([
                'mediumpurple',
                'mediumslateblue',
            ]),
            num_generations,
        )],
        width=1.0,
    )
    ax.set_xlabel('Position (Rank)')
    ax.set_ylabel('Absolute MRCA Uncertainty')
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

    if do_show: plt.show()

    return ax
