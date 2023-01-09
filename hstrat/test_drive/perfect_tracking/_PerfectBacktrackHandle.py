import typing


class PerfectBacktrackHandle:
    """Breadcrumb for perfectly backtracking a phylogenetic chain of descent.

    Because only backwards references are held, Python garbage collection takes
    care of pruning away extinct lineages.
    """

    parent: "PerfectBacktrackHandle"
    data: typing.Any

    def __init__(
        self: "PerfectBacktrackHandle",
        parent: "PerfectBacktrackHandle" = None,
        data: typing.Any = None,
    ) -> None:
        """Create backtracking breadcrumb, with `parent` as preceding
        breadcrumb in line of descent or `None` if associated with seed
        organism."""
        self.parent = parent
        self.data = data

    def CreateDescendant(
        self: "PerfectBacktrackHandle", data: typing.Any = None
    ) -> "PerfectBacktrackHandle":
        """Convenience factory method to create backtracking breadcrumbs
        succeeding `self` in line of descent."""
        cls = self.__class__
        return cls(self, data)
