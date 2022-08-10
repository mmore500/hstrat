from matplotlib import pyplot as plt
import typing
import seaborn as sns

from ..HereditaryStratigraphicColumn import HereditaryStratigraphicColumn

def strata_retained_frac_plot(
    stratum_retention_policy: typing.Any,
    num_generations: int,
    do_show: bool=True,
    axes: typing.Optional[plt.matplotlib.axes.Axes]=None,
) -> plt.matplotlib.axes.Axes:
    """Plot fraction deposited strata that are retained at each generation.

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
        xs,
        ys,
        ax=axes,
    )
    axes.set_xlabel('Generation')
    axes.set_ylabel('Frac Strata Retained')

    if do_show: plt.show()

    return axes
