import typing

from keyname import keyname as kn
from matplotlib import animation as mpl_animation
from matplotlib import pyplot as plt
from slugify import slugify
from tqdm import tqdm

from ..plot._stratum_retention_dripplot import stratum_retention_dripplot


def stratum_retention_animate(
    stratum_retention_policy: typing.Any,
    num_generations: int,
    do_show: bool = False,
    save_as: typing.Optional[str] = None,
    draw_extant_history: bool = True,
    draw_extinct_history: bool = True,
    draw_extinct_placeholders: bool = False,
) -> mpl_animation.FuncAnimation:
    """Animate evolution of strata histories under a stratum retention policy.

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
    fig = plt.figure(figsize=(6, 6), dpi=80)

    def update_func(frame) -> None:
        for ax in fig.axes:
            fig.delaxes(ax)
        fig.clear()
        ax = fig.add_subplot(111)
        stratum_retention_dripplot(
            stratum_retention_policy=stratum_retention_policy,
            num_generations=frame,
            do_show=False,
            ax=ax,
            draw_extant_history=draw_extant_history,
            draw_extinct_history=draw_extinct_history,
            draw_extinct_placeholders=draw_extinct_placeholders,
        )
        ax.set_aspect("equal")

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
                "a": "stratum_retention_dripplot",
                "extant_history": draw_extant_history,
                "extinct_history": draw_extinct_history,
                "extinct_placeholders": draw_extinct_placeholders,
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
