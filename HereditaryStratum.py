from bitarray import bitarray, frozenbitarray
import random


class HereditaryStratum:

    _deposition_rank: int
    _uid: frozenbitarray

    def __init__(
        self: 'HereditaryStratum',
        *,
        deposition_rank: int,
        uid_size: int=64,
    ):
        self._deposition_rank = deposition_rank
        self._uid = frozenbitarray(
            ''.join(random.choices('01', k=uid_size,))
        )

    def __eq__(
        self: 'HereditaryStratum',
        other: 'HereditaryStratum',
    ) -> bool:
        if isinstance(other, self.__class__,):
            return self.__dict__ == other.__dict__
        else:
            return False

    def GetDepositionRank(self: 'HereditaryStratum',) -> int:
        return self._deposition_rank

    def GetUid(self: 'HereditaryStratum',) -> frozenbitarray:
        return self._uid
