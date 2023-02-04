import typing


class PerfectBacktrackHandle:
    """Breadcrumb for perfectly backtracking a phylogenetic chain of descent.

    Because only backwards references are held, Python garbage collection takes
    care of pruning away extinct lineages.
    """

    # Achieves 60% the performance of C++ shared_ptr-based implementation in
    # tracking a unbranching linked list and outperforms the C++ implementation
    # by 30% in tracking a phylogenetic tree with random selection
    #
    #   p = [impl() for __ in range(100)]
    #   for __ in tqdm(range(10000000)):
    #       p[random.randrange(len(p))] = random.choice(p).CreateDescendant()
    #
    # see https://gist.github.com/mmore500/d6ee9011e38355f1be6c02a70db5b785
    # and https://gist.github.com/mmore500/71eb2f3f14afb02fba476dd2cea45210
    # (didn't complete debugging, but is representative of speed)

    # tried a dict-based database approach, but even with native implementaiton
    # was aboutt 3x slower than this approach
    # see https://gist.github.com/mmore500/7e9b85f005882d1e4b0206a9ef6d1de2

    parent: "PerfectBacktrackHandle"
    data: typing.Any

    __slots__ = ("parent", "data")

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
