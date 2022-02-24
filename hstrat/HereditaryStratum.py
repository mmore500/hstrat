import random
import typing


class HereditaryStratum:

    _deposition_rank: int
    _differentia: int
    _annotation: typing.Optional[typing.Any]

    def __init__(
        self: 'HereditaryStratum',
        *,
        deposition_rank: typing.Optional[int]=None,
        annotation: typing.Optional[typing.Any]=None,
        differentia_size: int=64,
    ):
        if deposition_rank is not None:
            self._deposition_rank = deposition_rank
        self._differentia = random.randrange(2**differentia_size)
        if annotation is not None:
            self._annotation = annotation

    def __eq__(
        self: 'HereditaryStratum',
        other: 'HereditaryStratum',
    ) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def GetDepositionRank(
        self: 'HereditaryStratum',
    ) -> typing.Optional[int]:
        if hasattr(self, '_deposition_rank'):
            return self._deposition_rank
        else: return None

    def GetDifferentia(self: 'HereditaryStratum') -> int:
        return self._differentia

    def GetAnnotation(self: 'HereditaryStratum') -> typing.Optional[typing.Any]:
        return self._annotation
