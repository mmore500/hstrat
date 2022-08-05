import typing


class PolicySpec:
    """Contains all policy parameters, if any."""

    _fixed_resolution: int

    def __init__(
        self: 'PolicySpec',
        fixed_resolution: int,
    ):
        """Construct the policy spec.

        Parameters
        ----------
        fixed_resolution : int
            The rank interval strata should be retained at. The uncertainty of
            MRCA estimates provided under the fixed resolution policy will
            always be strictly less than this cap.
        """

        assert fixed_resolution > 0
        self._fixed_resolution = fixed_resolution

    def __eq__(
        self: 'PolicySpec',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, PolicySpec) and (
            self._fixed_resolution,
        ) == (
            other._fixed_resolution,
        )
