from __future__ import annotations
from functools import reduce
from operator import and_, or_
from typing import TypeVar, Generic, Iterable

__all__ = ["ItemSet"]

E = TypeVar("E")


class ItemSet(Generic[E]):
    def __contains__(self, item: E) -> bool:
        """Return True if the ItemSet contains the given item"""
        raise NotImplementedError

    def __eq__(self, other: ItemSet[E]) -> bool:
        """Return the union of two ItemSets"""
        raise NotImplementedError

    def __or__(self, other: ItemSet[E]) -> ItemSet[E]:
        """Return the union of two ItemSets"""
        raise NotImplementedError

    def __and__(self, other: ItemSet[E]) -> ItemSet[E]:
        """Return the intersection of two ItemSets"""
        raise NotImplementedError

    def __ior__(self, other: ItemSet[E]) -> ItemSet[E]:
        """Return the union of two ItemSets"""
        return self | other

    def __iand__(self, other: ItemSet[E]) -> ItemSet[E]:
        """Return the intersection of two ItemSets"""
        return self & other

    def __invert__(self) -> ItemSet[E]:
        """Return the inversion of the ItemSet"""
        raise NotImplementedError

    def __hash__(self) -> int:
        """Return the hash of the ItemSet"""
        raise NotImplementedError

    @classmethod
    def intersection(cls, items: Iterable[ItemSet[E]]) -> ItemSet[E]:
        if items:
            return reduce(and_, items)
        else:
            return cls.always()

    @classmethod
    def union(cls, items: Iterable[ItemSet[E]]) -> ItemSet[E]:
        if items:
            return reduce(or_, items)
        else:
            return cls.never()

    @classmethod
    def never(cls) -> ItemSet[E]:
        raise NotImplementedError

    @classmethod
    def always(cls) -> ItemSet[E]:
        raise NotImplementedError

    @property
    def is_never(self) -> bool:
        """Return True is the ItemSet correspond to a never matching set"""
        raise NotImplementedError

    @property
    def is_always(self) -> bool:
        """Return True is the ItemSet correspond to an always matching set"""
        raise NotImplementedError
