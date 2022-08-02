from matplotlib import pyplot as plt
import typing


def stratum_retention_drip_plot(
    stratum_retention_predicate: typing.Callable[[int, int], bool],
    num_generations: int,
    do_show: bool=True,
    axes: typing.Optional[plt.matplotlib.axes.Axes]=None,
) -> plt.matplotlib.axes.Axes:
    """Plot position of retained strata within a hereditary stratigraphic
    column over successive depositions under a particular stratum retention
    policy.

    Parameters
    ----------
    stratum_retention_predicate: Callable
        Functor that implementing stratum retention policies by specifying
        whether a stratum with deposition rank r should be retained within
        a hereditary stratigraphic column after n strata have been
        deposited.
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

    for site in range(num_generations):
        for gen in range(site, num_generations):
            if not stratum_retention_predicate(site, gen):
                break
        axes.plot([site, site], [site, gen], 'k')

    axes.invert_yaxis()

    axes.set_xlabel('Column Position')
    axes.set_ylabel('Generation')

    if do_show: plt.show()

    return axes
