from __future__ import annotations
from typing import TypeVar, Generic, FrozenSet

from .ItemSet import ItemSet

__all__ = ["ItemSetSTD"]

E = TypeVar("E")


class ItemSetSTD(ItemSet, Generic[E]):
    def __init__(self, items: FrozenSet[E], inverted: bool = False):
        self.items: FrozenSet[E] = items
        self.inverted: bool = inverted

    def __contains__(self, item: E) -> bool:
        if self.inverted:
            return item not in self.items
        else:
            return item in self.items

    def __eq__(self, other: ItemSetSTD[E]) -> bool:
        return self.items == other.items and self.inverted == other.inverted

    def __or__(self, other: ItemSetSTD[E]) -> ItemSetSTD[E]:
        if self.inverted:
            if other.inverted:
                items = self.items.intersection(other.items)
            else:
                items = self.items.difference(other.items)
        else:
            if other.inverted:
                items = other.items.difference(self.items)
            else:
                items = other.items.union(self.items)

        return self.__class__(items, self.inverted or other.inverted)

    def __and__(self, other: ItemSetSTD[E]) -> ItemSetSTD[E]:
        if self.inverted:
            if other.inverted:
                items = other.items.union(self.items)
            else:
                items = other.items.difference(self.items)
        else:
            if other.inverted:
                items = self.items.difference(other.items)
            else:
                items = self.items.intersection(other.items)

        return self.__class__(items, self.inverted and other.inverted)

    def __invert__(self) -> ItemSetSTD[E]:
        return self.__class__(self.items, not self.inverted)

    def __truediv__(self, other: ItemSetSTD[E]) -> ItemSetSTD[E]:
        return self & ~other

    def __hash__(self) -> int:
        return hash((type(self), self.items, self.inverted))

    @classmethod
    def never(cls) -> ItemSetSTD[E]:
        return cls(frozenset(), False)

    @classmethod
    def always(cls) -> ItemSetSTD[E]:
        return cls(frozenset(), True)

    @property
    def is_never(self) -> bool:
        return not self.inverted and not self.items

    @property
    def is_always(self) -> bool:
        return self.inverted and not self.items
