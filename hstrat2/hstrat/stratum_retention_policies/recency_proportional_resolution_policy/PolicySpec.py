import typing


class PolicySpec:
    """Contains all policy parameters, if any."""

    _guaranteed_mrca_recency_proportional_resolution: int

    def __init__(
        self: 'PolicySpec',
        guaranteed_mrca_recency_proportional_resolution: int,
    ):
        """Construct the policy spec.

        Parameters
        ----------
        guaranteed_mrca_recency_proportional_resolution : int, optional
            The desired minimum number of intervals between the MRCA and the
            deeper compared column to be able to be distinguished between. The
            uncertainty of MRCA rank estimates provided under the MRCA-recency-
            proportional resolution policy will scale as the actual
            phylogenetic depth of the MRCA divided by
            guaranteed_mrca_recency_proportional_resolution.
        """

        self._guaranteed_mrca_recency_proportional_resolution \
            = guaranteed_mrca_recency_proportional_resolution

    def __eq__(
        self: 'PolicySpec',
        other: typing.Any,
    ) -> bool:
        return isinstance(other, self.__class__) and (
            self._guaranteed_mrca_recency_proportional_resolution,
        ) == (
            other._guaranteed_mrca_recency_proportional_resolution,
        )

    def __repr__(
        self: 'PolicySpec',
    ) -> str:
        return f'''{
            self.GetPolicyName()
        }.{
            PolicySpec.__qualname__
        }(guaranteed_mrca_recency_proportional_resolution={
            self._guaranteed_mrca_recency_proportional_resolution
        })'''

    @staticmethod
    def GetPolicyName() -> str:
        return __package__.split(".")[-1]

    @staticmethod
    def GetPolicyTitle() -> str:
        return "Recency-proportional Resolution Stratum Retention Policy"
