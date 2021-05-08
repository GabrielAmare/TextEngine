from __future__ import annotations
from functools import reduce
from operator import and_, or_, xor
from typing import TypeVar, Generic, FrozenSet, Iterable

from .ItemSetLocal import ItemSetLocal

__all__ = ["ItemSetGlobal"]

E = TypeVar("E")


class ItemSetGlobal(ItemSetLocal[E], Generic[E]):
    @classmethod
    def intersection(cls, items: Iterable[ItemSetGlobal[E]]) -> ItemSetGlobal[E]:
        if items:
            return reduce(and_, items)
        else:
            return cls.always()

    @classmethod
    def union(cls, items: Iterable[ItemSetGlobal[E]]) -> ItemSetGlobal[E]:
        if items:
            return reduce(or_, items)
        else:
            return cls.never()

    def __init__(self, items: FrozenSet[E], inverted: bool = False):
        super().__init__(items)
        self.inverted: bool = inverted

    def __contains__(self, item: E) -> bool:
        """Return True if the ItemSetGlobal contains the given item"""
        return xor(self.inverted, super().__contains__(item))

    def __eq__(self, other: ItemSetGlobal[E]) -> bool:
        """Return the union of two ItemSetGlobals"""
        return self.inverted == other.inverted and super().__eq__(other)

    def __add__(self, item: E) -> ItemSetLocal[E]:
        """Return a new ISL without the specified item included"""
        if self.inverted:
            return self.__class__(self.items.difference({item}))
        else:
            return self.__class__(self.items.union({item}))

    def __sub__(self, item: E) -> ItemSetLocal[E]:
        """Return a new ISL without the item not included"""
        if self.inverted:
            return self.__class__(self.items.union({item}))
        else:
            return self.__class__(self.items.difference({item}))

    def __or__(self, other: ItemSetGlobal[E]) -> ItemSetGlobal[E]:
        """Return the union of two ItemSetGlobals"""
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

    def __and__(self, other: ItemSetGlobal[E]) -> ItemSetGlobal[E]:
        """Return the intersection of two ItemSetGlobals"""
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

    def __invert__(self) -> ItemSetGlobal[E]:
        """Return the inversion of the ItemSetGlobal"""
        return self.__class__(self.items, not self.inverted)

    def __hash__(self) -> int:
        """Return the hash of the ItemSetGlobal"""
        return hash((type(self), self.items, self.inverted))

    @classmethod
    def never(cls) -> ItemSetGlobal[E]:
        return cls(frozenset(), False)

    @property
    def is_never(self) -> bool:
        """Return True is the ItemSetGlobal correspond to a never matching set"""
        return not self.inverted and not self.items

    @classmethod
    def always(cls) -> ItemSetGlobal[E]:
        return cls(frozenset(), True)

    @property
    def is_always(self) -> bool:
        """Return True is the ItemSetGlobal correspond to an always matching set"""
        return self.inverted and not self.items
