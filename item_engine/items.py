from dataclasses import dataclass
from typing import FrozenSet, Type

import python_generator as pg

__all__ = ("Item", "AnyOther", "Group", "ALWAYS", "NEVER")


@dataclass(frozen=True, order=True)
class Item:
    @property
    def as_group(self):
        raise NotImplementedError

    def __or__(self, other):
        return self.as_group | other

    __ior__ = __or__


@dataclass(frozen=True, order=True)
class AnyOther(Item):
    pass


@dataclass(frozen=True, order=True)
class Group:
    items: FrozenSet[Item]
    inverted: bool = False

    def __contains__(self, item):
        if self.inverted:
            return item not in self.items
        else:
            return item in self.items

    def __invert__(self):
        return self.__class__(self.items, not self.inverted)

    def __truediv__(self, other):
        assert isinstance(other, Group)
        return self & ~other

    def __and__(self, other):
        assert isinstance(other, Group)
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

    def __or__(self, other):
        assert isinstance(other, Group)
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

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return self.items

    @property
    def condition(self) -> pg.CONDITION:
        raise NotImplementedError

    @property
    def code_factory(self) -> Type[pg.CONDITION]:
        if len(self.items) == 1:
            if self.inverted:
                return pg.NE
            else:
                return pg.EQ
        else:
            if self.inverted:
                return pg.NOT_IN
            else:
                return pg.IN


ALWAYS = Group(frozenset(), True)
NEVER = Group(frozenset(), False)
