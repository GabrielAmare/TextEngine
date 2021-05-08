from __future__ import annotations
from dataclasses import dataclass
from typing import Union, List

from item_engine import Item, Group, Match
import python_generator as pg

__all__ = ["CharI", "CharG", "TokenI", "TokenG"]


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


class TokenG(Group):
    @property
    def items_str(self) -> str:
        return '\n'.join(map(repr, sorted([item.name for item in self.items])))

    @property
    def condition(self) -> pg.CONDITION:
        items = sorted(map(str, self.items))
        grp = items[0] if len(self.items) == 1 else pg.TUPLE(items)
        return self.code_factory("item.value", grp)

    def match(self, action: str) -> Match:
        return Match(self, action)

    @classmethod
    def grp(cls, names: Union[str, List[str]]) -> TokenG:
        if isinstance(names, str):
            names = [names]
        return cls(frozenset(map(TokenI, names)))


@dataclass(frozen=True, order=True)
class CharI(Item):
    char: str

    def __str__(self):
        return self.char

    @property
    def as_group(self) -> CharG:
        return CharG(frozenset({self}))


@dataclass(frozen=True, order=True)
class TokenI(Item):
    name: str

    def __str__(self):
        return repr(self.name)

    @property
    def as_group(self) -> TokenG:
        return TokenG(frozenset({self}))
