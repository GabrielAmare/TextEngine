from __future__ import annotations
from typing import TypeVar, Generic, FrozenSet, Iterable, Type

__all__ = ["Item", "ItemSet"]


class Item:
    def __hash__(self):
        raise NotImplementedError

    @property
    def as_group(self) -> ItemSet:
        raise NotImplementedError

    def __or__(self, other: ItemSet) -> ItemSet:
        return self.as_group | other

    __ior__ = __or__

    def __add__(self, other: Item):
        return self.as_group + other

    __iadd__ = __add__


E = TypeVar("E", bound=Item)
T = TypeVar("T")


class ItemSet(Generic[E]):
    @classmethod
    def never(cls: Type[T]) -> T[E]:
        """return ∅"""
        return cls(frozenset(), False)

    @classmethod
    def always(cls: Type[T]) -> T[E]:
        """return Ω"""
        return cls(frozenset(), True)

    def __init__(self, items: Iterable[E], inverted: bool = False):
        self.items: FrozenSet[E] = frozenset(items)
        self.inverted: bool = inverted

    def __repr__(self) -> str:
        """return repr(self)"""
        return f"{self.__class__.__name__}({self.items!r}, {self.inverted!r})"

    @property
    def items_str(self) -> str:
        return str(self.items)

    def __str__(self) -> str:
        """return str(self)"""
        if self.items:
            return f"{'¬' if self.inverted else ''}{self.items_str}"
        else:
            return 'Ω' if self.inverted else '∅'

    def __hash__(self) -> int:
        """return hash(self)"""
        return hash((type(self), self.items, self.inverted))

    def __contains__(self, obj: E) -> bool:
        """return obj in self"""
        if self.inverted:
            return obj not in self.items
        else:
            return obj in self.items

    def __eq__(self: T[E], other: T[E]) -> bool:
        return self.inverted == other.inverted and self.items == other.items

    def __ne__(self: T[E], other: T[E]) -> bool:
        """return self != other"""
        return not (self == other)

    def __lt__(self: T[E], other: T[E]) -> bool:
        """return self < other"""
        return self != other and self <= other

    def __le__(self: T[E], other: T[E]) -> bool:
        """return self <= other"""
        return (self / other).is_never

    def __gt__(self: T[E], other: T[E]) -> bool:
        """return self > other"""
        return other < self

    def __ge__(self: T[E], other: T[E]) -> bool:
        """return self >= other"""
        return other <= self

    def __or__(self: T[E], other: T[E]) -> T[E]:
        """return self | other"""
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

    __ior__ = __or__

    def __and__(self: T[E], other: T[E]) -> T[E]:
        """return self & other"""
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

    __iand__ = __and__

    def __truediv__(self: T[E], other: T[E]) -> T[E]:
        """return self / other"""
        if self.inverted:
            if other.inverted:
                items = other.items.difference(self.items)
            else:
                items = other.items.union(self.items)
        else:
            if other.inverted:
                items = self.items.intersection(other.items)
            else:
                items = self.items.difference(other.items)

        return self.__class__(items, self.inverted and not other.inverted)

    __itruediv__ = __truediv__

    def __add__(self: T[E], other: E) -> T[E]:
        """return self + other"""
        return self | other.as_group

    __iadd__ = __add__

    def __sub__(self: T[E], other: E) -> T[E]:
        """return self - other"""
        return self / other.as_group

    __isub__ = __sub__

    def __invert__(self: T[E]) -> T[E]:
        """return ~self"""
        return self.__class__(self.items, not self.inverted)

    @property
    def is_never(self) -> bool:
        """return self == ∅"""
        return not self.inverted and not self.items

    @property
    def is_always(self) -> bool:
        """return self == Ω"""
        return self.inverted and not self.items
