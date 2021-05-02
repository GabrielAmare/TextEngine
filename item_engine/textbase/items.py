from dataclasses import dataclass
from item_engine import Item, Group, Match
import python_generator as pg

__all__ = ["CharI", "CharG", "TokenI", "TokenG"]


@dataclass(frozen=True, order=True)
class CharG(Group):
    @property
    def condition(self) -> pg.CONDITION:
        expr = ''.join(sorted(map(str, self.items)))
        return self.code_factory("item.char", repr(expr))

    def match(self, action: str) -> Match:
        return Match(self, action)

    def inc(self):
        return self.match("include")

    def exc(self):
        return self.match("ignore")


@dataclass(frozen=True, order=True)
class TokenG(Group):
    @property
    def condition(self) -> pg.CONDITION:
        items = sorted(map(str, self.items))
        grp = items[0] if len(self.items) == 1 else pg.TUPLE(items)
        return self.code_factory("item.value", grp)

    def match(self, action: str) -> Match:
        return Match(self, action)

    def inc(self):
        return self.match("include")

    def exc(self):
        return self.match("ignore")

    def as_(self, key):
        return self.match(f"as:{key!s}")

    def in_(self, key):
        return self.match(f"in:{key!s}")


@dataclass(frozen=True, order=True)
class CharI(Item):
    char: str

    def __str__(self):
        return self.char

    @property
    def as_group(self):
        return CharG(frozenset({self}))

    def match(self, action: str) -> Match:
        return self.as_group.match(action)

    def inc(self):
        return self.match("include")

    def exc(self):
        return self.match("ignore")


@dataclass(frozen=True, order=True)
class TokenI(Item):
    name: str

    def __str__(self):
        return repr(self.name)

    @property
    def as_group(self):
        return TokenG(frozenset({self}))

    def match(self, action: str) -> Match:
        return self.as_group.match(action)

    def inc(self):
        return self.match("include")

    def exc(self):
        return self.match("ignore")

    def as_(self, key):
        return self.match(f"as:{key!s}")

    def in_(self, key):
        return self.match(f"in:{key!s}")
