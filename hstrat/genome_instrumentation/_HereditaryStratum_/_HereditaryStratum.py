import operator
import random
import typing


class HereditaryStratum:
    """Packages stratigraph data associated with a particular generation.

    Includes differentia "fingerprint" associated with a particular
    generation of a line of descent and possibly additional metadata, including
    optional user-provided annotation.
    """

    __slots__ = (
        "_deposition_rank",
        "_differentia",
        "_annotation",
    )

    _deposition_rank: int
    # random "fingerprint" generated at initialization
    _differentia: int
    # optional arbitrary user-provided data
    _annotation: typing.Optional[typing.Any]

    def __init__(
        self: "HereditaryStratum",
        *,
        annotation: typing.Optional[typing.Any] = None,
        differentia_bit_width: int = 64,
        deposition_rank: typing.Optional[int] = None,
        differentia: typing.Optional[int] = None,
    ):
        """Construct the stratum.

        Randomly generates and stores a differentia "fingerprint" alongside
        other metadata, if provided.

        Parameters
        ----------
        annotation: any, optional
            Optional object to store as an annotation. Allows arbitrary user-
            provided to be associated with this stratum's generation in its
            line of descent.
        differentia_bit_width: int, optional
            The bit width of the generated differentia. Default 64, allowing
            for 2^64 distinct values.
        deposition_rank : int, optional
            The position of the stratum being deposited within the sequence of strata deposited into the column. Precisely, the number of strata that have been deposited before stratum.
        """
        if differentia is not None:
            if differentia_bit_width is not None:
                assert differentia < 2**differentia_bit_width
            self._differentia = differentia
        else:
            self._differentia = random.randrange(2**differentia_bit_width)

        self._annotation = annotation
        self._deposition_rank = deposition_rank

    def __eq__(self: "HereditaryStratum", other: "HereditaryStratum") -> bool:
        """Compare for value-wise equality."""
        # adapted from https://stackoverflow.com/a/4522896
        return (
            isinstance(
                other,
                self.__class__,
            )
            and self.__slots__ == other.__slots__
            and all(
                getter(self) == getter(other)
                for getter in [
                    operator.attrgetter(attr) for attr in self.__slots__
                ]
            )
        )

    def GetDepositionRank(self: "HereditaryStratum") -> typing.Optional[int]:
        """Get the deposition order rank associated with this stratum, if stored.

        Deposition rank is the number of strata deposited on a column before
        self. Deposition rank may not be stored if the stratum retention policy
        supports calculation of deposition rank from column index.
        """
        if hasattr(self, "_deposition_rank"):
            return self._deposition_rank
        else:
            return None

    def GetDifferentia(self: "HereditaryStratum") -> int:
        """Access differentia.

        Returns the randomly-generated value that distinguishes this stratum
        from others generated at the same rank in other hereditary columns.
        """
        return self._differentia

    def GetAnnotation(
        self: "HereditaryStratum",
    ) -> typing.Optional[typing.Any]:
        """Access arbitrary, user-specified annotation, if any."""
        return self._annotation
