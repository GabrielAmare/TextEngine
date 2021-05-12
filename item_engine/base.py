from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Iterator, FrozenSet, List, TypeVar, Generic, Type
from functools import reduce
from operator import and_

from .constants import ACTION, INCLUDE, EXCLUDE, AS, IN
from .generic_items import GenericItem, GenericItemSet
import python_generator as pg

INF = -1

__all__ = [
    "INF",
    "Rule",
    "Empty", "RuleUnit", "RuleList",
    "Optional", "Repeat", "All", "Any",
    "Match",
]


def alphabet(self: Rule) -> FrozenSet[Item]:
    """
        Return a frozenset containing all the explicit items of a given rule
        It is possible that an item matches a rule without being in it's alphabet,
        this case occurs when the rule contains at some level a Match which has an inverted Group.
    """
    if isinstance(self, Empty):
        return frozenset()
    elif isinstance(self, RuleUnit):
        return alphabet(self.rule)
    elif isinstance(self, RuleList):
        return frozenset({item for rule in self.rules for item in alphabet(rule)})
    elif isinstance(self, Match):
        return self.group.items
    else:
        raise ValueError(self)


def is_valid(self: Rule) -> bool:
    """Return True when a Rule is valid"""
    if isinstance(self, Empty):
        return self.valid
    elif isinstance(self, All):
        return len(self.rules) == 1 and is_valid(self.rules[0])
    elif isinstance(self, Any):
        return all(map(is_valid, self.rules))
    else:
        return False


def is_error(self: Rule) -> bool:
    """Return True when a Rule is error"""
    if isinstance(self, Empty):
        return not self.valid
    elif isinstance(self, All):
        return len(self.rules) == 1 and is_error(self.rules[0])
    elif isinstance(self, Any):
        return all(map(is_error, self.rules))
    else:
        return False


def is_terminal(self: Rule) -> bool:
    """Return True when a Rule is terminal"""
    if isinstance(self, Empty):
        return True
    elif isinstance(self, All):
        return len(self.rules) == 1 and is_terminal(self.rules[0])
    elif isinstance(self, Any):
        return all(map(is_terminal, self.rules))
    else:
        return False


def is_skipable(self: Rule) -> bool:
    """Return True when a Rule is skipable"""
    if isinstance(self, (Optional, Repeat)):
        return True
    elif isinstance(self, All):
        return all(map(is_skipable, self.rules))
    elif isinstance(self, Any):
        return any(map(is_skipable, self.rules))
    else:
        return False


def decompose_all(self: All) -> Iterator[Tuple[Rule, Rule]]:
    for index, rule in enumerate(self.rules):
        if index + 1 < len(self.rules):
            yield rule, reduce(and_, self.rules[1:])
        else:
            yield rule, Empty(valid=True)

        if not rule.skipable:
            break


def splited(self: Rule) -> Iterator[Tuple[Match, Rule]]:
    """
        Split the rules by returning a Match followed by the remaining Rule after the Match
    """
    if isinstance(self, Empty):
        if is_valid(self):
            yield Match(group=Group.always(), action=EXCLUDE), self
        else:
            yield Match(group=Group.never(), action=EXCLUDE), self
    elif isinstance(self, Optional):
        for first, after in splited(self.rule):
            yield first, after
    elif isinstance(self, Repeat):
        for first, after in splited(self.rule):
            yield first, after & self
    elif isinstance(self, All):
        for rule_first, rule_after in decompose_all(self):
            for first, after in splited(rule_first):
                yield first, after & rule_after
    elif isinstance(self, Any):
        for rule in self.rules:
            for first, after in splited(rule):
                yield first, after
    elif isinstance(self, Match):
        yield self, Empty(valid=True)
        yield Match(~self.group, EXCLUDE), Empty(valid=False)
    else:
        raise ValueError(self)


########################################################################################################################
# Rule
########################################################################################################################

@dataclass(frozen=True, order=True)
class Rule:
    def repeat(self, mn: int = 0, mx: int = INF) -> Rule:
        assert mn >= 0
        assert mx == -1 or (mx >= mn and mx > 0)

        if mn == 0:
            base = Empty(valid=True)
        else:
            base = All(tuple(mn * self.all))

        if mx == INF:
            return base & Repeat(self)
        else:
            return base & All(tuple((mx - mn) * self.all))

    @property
    def optional(self) -> Optional:
        return Optional(self)

    @property
    def all(self) -> List[Rule]:
        return list(self.rules) if isinstance(self, All) else [self]

    @property
    def any(self) -> List[Rule]:
        return list(self.rules) if isinstance(self, Any) else [self]

    def __and__(self, other: Rule) -> Rule:
        if isinstance(self, Empty):
            return other if self.valid else self

        if isinstance(other, Empty):
            return self if other.valid else other

        return All(tuple(self.all + other.all))

    def __or__(self, other) -> Rule:
        if isinstance(self, Empty):
            return other

        if isinstance(other, Empty):
            return self

        return Any(tuple(self.any + other.any))

    is_valid = property(is_valid)
    is_error = property(is_error)
    alphabet = property(alphabet)
    terminal = is_terminal = property(is_terminal)
    skipable = is_skipable = property(is_skipable)
    splited = property(splited)


########################################################################################################################
# Empty | RuleUnit | RuleList
########################################################################################################################

@dataclass(frozen=True, order=True)
class Empty(Rule):
    valid: bool


@dataclass(frozen=True, order=True)
class RuleUnit(Rule):
    rule: Rule


@dataclass(frozen=True, order=True)
class RuleList(Rule):
    rules: Tuple[Rule, ...]

    def __iter__(self) -> Iterator[Rule]:
        return iter(self.rules)

    def __len__(self) -> int:
        return len(self.rules)


########################################################################################################################
# Optional | Repeat | All | Any
########################################################################################################################

@dataclass(frozen=True, order=True)
class Optional(RuleUnit):
    pass


@dataclass(frozen=True, order=True)
class Repeat(RuleUnit):
    pass


@dataclass(frozen=True, order=True)
class All(RuleList):
    pass


@dataclass(frozen=True, order=True)
class Any(RuleList):
    pass


########################################################################################################################
# Match
########################################################################################################################


@dataclass(frozen=True, order=True)
class Match(Rule):
    """When an item is validated by the ``group``, the action will be done"""
    group: Group
    action: ACTION = ""


__all__ += ["Item", "Group"]


class ItemInterface:
    def match(self, action: ACTION) -> Match:
        if isinstance(self, Item):
            return Match(self.as_group, action)
        elif isinstance(self, Group):
            return Match(self, action)
        else:
            raise ValueError(self)

    def include(self) -> Match:
        return self.match(INCLUDE)

    def exclude(self) -> Match:
        return self.match(EXCLUDE)

    def include_as(self, key: str) -> Match:
        return self.match(AS.format(key))

    def include_in(self, key: str) -> Match:
        return self.match(IN.format(key))

    inc = include
    exc = exclude
    as_ = include_as
    in_ = include_in


@dataclass(frozen=True, order=True)
class Item(GenericItem, ItemInterface):
    @property
    def as_group(self) -> Group:
        raise NotImplementedError


E = TypeVar("E", bound=Item)


class Group(GenericItemSet[E], Generic[E], ItemInterface):
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

    @property
    def condition(self) -> pg.CONDITION:
        raise NotImplementedError
