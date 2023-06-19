import typing

from keyname import keyname as kn
from matplotlib import animation as mpl_animation
from matplotlib import pyplot as plt
from slugify import slugify
from tqdm import tqdm

from ..plot._policy_panel_plot import policy_panel_plot


def policy_panel_animate(
    stratum_retention_policy: typing.Any,
    num_generations: int,
    do_show: bool = False,
    save_as: typing.Optional[str] = None,
) -> mpl_animation.FuncAnimation:
    """Animate evolution of column and its properties under a retention policy.

    Parameters
    ----------
    stratum_retention_policy : any
        Object specifying stratum retention policy.
    num_generations : int
        Number of generations to plot.
    do_show : bool, optional
        Whether to show() the plot automatically.
    save_as : str, optional
        If set, save animation as file type specified.
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

    res = mpl_animation.FuncAnimation(
        fig,
        update_func,
        frames=range(num_generations),
        interval=500,
        blit=False,
    )

    if save_as is not None:
        fname = kn.pack(
            {
                "a": "policy_panel_plot",
                "num_generations": num_generations,
                "policy": slugify(str(stratum_retention_policy)),
                "ext": f'.{save_as.strip(".")}',
            }
        )
        print(f"saving animation to {fname}")
        progress = tqdm(total=num_generations)
        res.save(
            fname,
            fps=5,
            writer="imagemagick",
            progress_callback=lambda *args, **kwargs: progress.update(),
        )

    if do_show:
        plt.show()

    return res
