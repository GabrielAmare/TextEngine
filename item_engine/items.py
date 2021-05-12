from __future__ import annotations
from dataclasses import dataclass
from typing import FrozenSet, Type, TypeVar, Generic

import python_generator as pg

__all__ = ["Item", "AnyOther", "Group"]

from .generic_items import GenericItem, GenericItemSet
from .constants import INCLUDE, EXCLUDE, AS, IN


@dataclass(frozen=True, order=True)
class Item(GenericItem):
    @property
    def as_group(self) -> Group:
        raise NotImplementedError

    def match(self, action: str):
        return self.as_group.match(action)

    def inc(self):
        return self.as_group.inc()

    def exc(self):
        return self.as_group.exc()

    def as_(self, key):
        return self.as_group.as_(key)

    def in_(self, key):
        return self.as_group.in_(key)


@dataclass(frozen=True, order=True)
class AnyOther(Item):
    pass


E = TypeVar("E", bound=Item)


class Group(GenericItemSet[E], Generic[E]):
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

    def match(self, action: str):
        raise NotImplementedError

    def inc(self):
        return self.match(INCLUDE)

    def exc(self):
        return self.match(EXCLUDE)

    def as_(self, key):
        return self.match(AS.format(key))

    def in_(self, key):
        return self.match(IN.format(key))
