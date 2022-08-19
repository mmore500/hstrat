import colorsys
import typing

import matplotlib as mpl


# adapted from https://stackoverflow.com/a/49601444
def scale_luminosity(
    color: typing.Union[typing.Tuple[float, float, float], str],
    amount: float,
) -> typing.Tuple[float, float, float]:
    """Lighten or darken a given color.

    Multiplies luminosity by the given amount. Input can be matplotlib color
    string, hex string, or RGB tuple.

    Examples
    --------
    >> scale_luminosity('g', 0.3)
    >> scale_luminosity('#F034A3', 0.6)
    >> scale_luminosity((.3,.55,.1), 0.5)
    """
    try:
        c = mpl.colors.cnames[color]
    except KeyError:
        c = color
    c = colorsys.rgb_to_hls(*mpl.colors.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])
