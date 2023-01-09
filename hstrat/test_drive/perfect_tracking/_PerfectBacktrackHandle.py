import typing


class PerfectBacktrackHandle:

    parent: "PerfectBacktrackHandle"
    data: typing.Any

    def __init__(
        self: "PerfectBacktrackHandle",
        parent: "PerfectBacktrackHandle" = None,
        data: typing.Any = None,
    ) -> None:
        self.parent = parent
        self.data = data

    def CreateDescendant(
        self: "PerfectBacktrackHandle", data: typing.Any = None
    ) -> "PerfectBacktrackHandle":
        cls = self.__class__
        return cls(self, data)
