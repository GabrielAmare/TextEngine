from __future__ import annotations
from dataclasses import dataclass

from item_engine import Item, Group, Match
import python_generator as pg

__all__ = ["CharI", "CharG"]


class CharG(Group):
    @property
    def items_str(self) -> str:
        return repr(''.join(sorted(repr(str(item))[1:-1] for item in self.items)))

    @property
    def condition(self) -> pg.CONDITION:
        expr = ''.join(sorted(map(str, self.items)))
        return self.code_factory("item.value", repr(expr))

    def match(self, action: str) -> Match:
        return Match(self, action)


@dataclass(frozen=True, order=True)
class CharI(Item):
    char: str

    def __str__(self):
        return self.char

    @property
    def as_group(self) -> CharG:
        return CharG(frozenset({self}))
