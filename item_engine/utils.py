from collections import deque
from typing import TypeVar, Generic, Deque, Iterator, Dict, Tuple, Iterable

K = TypeVar("K")

__all__ = ["Pile", "PositionRegister", "SetList"]


class SetList(list, Generic[K]):
    def append(self, object: K) -> None:
        if object not in self:
            super().append(object)

    def extend(self, iterable: Iterable[K]) -> None:
        for object in iterable:
            self.append(object)


class Pile(Generic[K]):
    def __init__(self, *data: K):
        self.data: Deque[K] = deque(data)
        self.length = len(data)

    def __contains__(self, item: K) -> bool:
        return item in self.data

    def __iter__(self) -> Iterator[K]:
        while self.length > 0:
            yield self.data.popleft()
            self.length -= 1

    def append(self, item: K) -> None:
        self.length += 1
        self.data.append(item)


INDEX = TypeVar("INDEX")
POSITION = TypeVar("POSITION")


class PositionRegister(Generic[INDEX, POSITION]):
    def __init__(self):
        self.positions: Dict[INDEX, POSITION] = {}

    def new(self) -> POSITION:
        if self.positions:
            return max(self.positions.values()) + 1
        else:
            return 0

    def get(self, index: INDEX) -> POSITION:
        if index in self.positions:
            return self.positions[index]
        else:
            self.positions[index] = position = self.new()
            return position

    def merge(self, p1: POSITION, p2: POSITION) -> Tuple[POSITION, POSITION]:
        """
            With ``mn``/``mx`` resp. the minimum/maximum of ``p1`` and ``p2``
            For any index pointing at position ``mn``, make it point to ``mx``
        """
        mx = max(p1, p2)
        mn = min(p1, p2)
        for index, position in self.positions.items():
            if position == mn:
                self.positions[index] = mx
        return mn, mx
