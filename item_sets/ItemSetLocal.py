from __future__ import annotations
from functools import reduce
from operator import and_, or_
from typing import TypeVar, Generic, Iterable, FrozenSet

from .ItemSet import ItemSet

__all__ = ["ItemSetLocal"]

E = TypeVar("E")


class ItemSetLocal(ItemSet, Generic[E]):
    def __init__(self, items: FrozenSet[E]):
        self.items = items

    def __repr__(self):
        return f"{self.__class__.__name__}({self.items!r})"

    def __contains__(self, item: E) -> bool:
        """Return True if the ItemSetLocal contains the given item"""
        return item in self.items

    def __eq__(self, other: ItemSetLocal[E]) -> bool:
        """Return the union of two ItemSetLocals"""
        return self.items == other.items

    def __add__(self, item: E) -> ItemSetLocal[E]:
        """Return a new ISL without the specified item included"""
        return self.__class__(self.items.union({item}))

    def __sub__(self, item: E) -> ItemSetLocal[E]:
        """Return a new ISL without the item not included"""
        return self.__class__(self.items.difference({item}))

    def __or__(self, other: ItemSetLocal[E]) -> ItemSetLocal[E]:
        """Return the union of two ItemSetLocals"""
        return self.__class__(self.items.union(other.items))

    def __ior__(self, other: ItemSetLocal[E]) -> ItemSetLocal[E]:
        """Return the union of two ItemSetLocals"""
        return self | other

    def __and__(self, other: ItemSetLocal[E]) -> ItemSetLocal[E]:
        """Return the intersection of two ItemSetLocals"""
        return self.__class__(self.items.intersection(other.items))

    def __iand__(self, other: ItemSetLocal[E]) -> ItemSetLocal[E]:
        """Return the intersection of two ItemSetLocals"""
        return self & other

    def __invert__(self) -> ItemSetLocal[E]:
        """Return the inversion of the ItemSetGlobal"""
        raise Exception("ItemSetLocal doesn't admit inversion")

    def __hash__(self) -> int:
        """Return the hash of the ItemSetLocal"""
        return hash((type(self), self.items))

    @classmethod
    def intersection(cls, items: Iterable[ItemSetLocal[E]]) -> ItemSetLocal[E]:
        if items:
            return reduce(and_, items)
        else:
            return cls.always()

    @classmethod
    def union(cls, items: Iterable[ItemSetLocal[E]]) -> ItemSetLocal[E]:
        if items:
            return reduce(or_, items)
        else:
            return cls.never()

    @classmethod
    def never(cls) -> ItemSetLocal[E]:
        return cls(frozenset())

    @property
    def is_never(self) -> bool:
        """Return True is the ItemSetLocal correspond to a never matching set"""
        return not self.items

    @classmethod
    def always(cls) -> ItemSetLocal[E]:
        raise Exception(f"ItemSetLocal doesn't admit always instances")

    @property
    def is_always(self) -> bool:
        """Return True is the ItemSetLocal correspond to an always matching set"""
        return False
