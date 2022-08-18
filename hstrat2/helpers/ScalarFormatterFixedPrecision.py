import matplotlib as mpl


# adapted from https://stackoverflow.com/a/42156450
class ScalarFormatterFixedPrecision(mpl.ticker.ScalarFormatter):

    _precision: int

    def __init__(
        self: "ScalarFormatterFixedPrecision",
        precision: int = 1,
    ) -> None:
        super(ScalarFormatterFixedPrecision, self).__init__()
        self._precision = precision

    # Override function that finds format to use.
    def _set_format(
        self: "ScalarFormatterFixedPrecision",
    ) -> None:
        self.format = "%.1f"
