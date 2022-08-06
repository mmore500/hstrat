import random
import typing


class HereditaryStratum:
    """Struct to package differentia "fingerprint" associated with a particular
    generation of a line of descent with additional metadata, including
    optional user-provided annotation."""

    _deposition_rank: int
    # random "fingerprint" generated at initialization
    _differentia: int
    # optional arbitrary user-provided data
    _annotation: typing.Optional[typing.Any]

    def __init__(
        self: 'HereditaryStratum',
        *,
        annotation: typing.Optional[typing.Any]=None,
        differentia_bit_width: int=64,
        deposition_rank: typing.Optional[int]=None,
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

        if deposition_rank is not None:
            self._deposition_rank = deposition_rank
        self._differentia = random.randrange(2**differentia_bit_width)
        if annotation is not None:
            self._annotation = annotation

    def __eq__(
        self: 'HereditaryStratum',
        other: 'HereditaryStratum',
    ) -> bool:
        """Compare for value-wise equality."""

        return isinstance(
            other,
            self.__class__,
        ) and self.__dict__ == other.__dict__

    def GetDepositionRank(
        self: 'HereditaryStratum',
    ) -> typing.Optional[int]:
        """Get the deposition order rank associated with this stratum, if stored.

        Deposition rank is the number of strata deposited on a column before
        self. Deposition rank may not be stored if the stratum retention policy
        supports calculation of deposition rank from column index.
        """

        if hasattr(self, '_deposition_rank'):
            return self._deposition_rank
        else: return None

    def GetDifferentia(self: 'HereditaryStratum') -> int:
        """Accessor for randomly-generated value distinguishing this stratum
        from others generated at the same rank in other hereditary columns."""

        return self._differentia

    def GetAnnotation(self: 'HereditaryStratum') -> typing.Optional[typing.Any]:
        """Accessor for arbitrary, user-specified data provided when stratum
        was deposited, if any."""

        return self._annotation
