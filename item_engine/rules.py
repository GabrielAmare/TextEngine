from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Iterator, FrozenSet, List
from functools import reduce
from operator import and_

from .items import Item, Group
from .constants import EXCLUDE

INF = -1

__all__ = [
    "INF",
    "Rule",
    "Empty", "RuleUnit", "RuleList",
    "Optional", "Repeat", "All", "Any",
    "Match",
]


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

    @property
    def is_valid(self) -> bool:
        return False

    @property
    def is_error(self) -> bool:
        return False

    def __and__(self, other: Rule) -> Rule:
        if self.is_error or other.is_valid:
            return self

        if self.is_valid or other.is_error:
            return other

        return All(tuple(self.all + other.all))

    def __or__(self, other) -> Rule:
        if isinstance(self, Empty):
            return other

        if isinstance(other, Empty):
            return self

        return Any(tuple(self.any + other.any))

    @property
    def alphabet(self) -> FrozenSet[Item]:
        raise NotImplementedError

    @property
    def terminal(self) -> bool:
        raise NotImplementedError

    @property
    def skipable(self) -> bool:
        raise NotImplementedError

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        raise NotImplementedError


########################################################################################################################
# Empty | RuleUnit | RuleList
########################################################################################################################

@dataclass(frozen=True, order=True)
class Empty(Rule):
    valid: bool

    @property
    def is_valid(self) -> bool:
        return self.valid

    @property
    def is_error(self) -> bool:
        return not self.valid

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return frozenset()

    @property
    def terminal(self) -> bool:
        return True

    @property
    def skipable(self) -> bool:
        return False

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        if self.valid:
            yield Match(group=Group.always(), action=EXCLUDE), self
        else:
            yield Match(group=Group.never(), action=EXCLUDE), self


@dataclass(frozen=True, order=True)
class RuleUnit(Rule):
    rule: Rule

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return self.rule.alphabet

    @property
    def terminal(self) -> bool:
        raise NotImplementedError

    @property
    def skipable(self) -> bool:
        raise NotImplementedError

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        raise NotImplementedError


@dataclass(frozen=True, order=True)
class RuleList(Rule):
    rules: Tuple[Rule, ...]

    def __iter__(self) -> Iterator[Rule]:
        return iter(self.rules)

    def __len__(self) -> int:
        return len(self.rules)

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return frozenset({item for rule in self.rules for item in rule.alphabet})

    @property
    def terminal(self) -> bool:
        raise NotImplementedError

    @property
    def skipable(self) -> bool:
        raise NotImplementedError

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        raise NotImplementedError


########################################################################################################################
# Optional | Repeat | All | Any
########################################################################################################################

@dataclass(frozen=True, order=True)
class Optional(RuleUnit):
    @property
    def terminal(self) -> bool:
        return False

    @property
    def skipable(self) -> bool:
        return True

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for first, after in self.rule.splited:
            yield first, after


@dataclass(frozen=True, order=True)
class Repeat(RuleUnit):
    @property
    def terminal(self) -> bool:
        return False

    @property
    def skipable(self) -> bool:
        return True

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for first, after in self.rule.splited:
            yield first, after & self


@dataclass(frozen=True, order=True)
class All(RuleList):
    @property
    def decomposed(self) -> Iterator[Tuple[Rule, Rule]]:
        for index, rule in enumerate(self.rules):
            if index + 1 < len(self.rules):
                yield rule, reduce(and_, self.rules[1:])
            else:
                yield rule, Empty(valid=True)

            if not rule.skipable:
                break

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for rule_first, rule_after in self.decomposed:
            for first, after in rule_first.splited:
                yield first, after & rule_after

    @property
    def skipable(self) -> bool:
        return all(rule.skipable for rule in self.rules)

    @property
    def terminal(self) -> bool:
        return len(self.rules) == 1 and self.rules[0].terminal

    @property
    def is_valid(self) -> bool:
        return len(self.rules) == 1 and self.rules[0].is_valid

    @property
    def is_error(self) -> bool:
        return len(self.rules) == 1 and self.rules[0].is_error


@dataclass(frozen=True, order=True)
class Any(RuleList):
    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for rule in self.rules:
            for first, after in rule.splited:
                yield first, after

    @property
    def skipable(self) -> bool:
        return any(rule.skipable for rule in self.rules)

    @property
    def terminal(self) -> bool:
        return all(rule.terminal for rule in self.rules)

    @property
    def is_valid(self) -> bool:
        return all(rule.is_valid for rule in self.rules)

    @property
    def is_error(self) -> bool:
        return all(rule.is_error for rule in self.rules)


########################################################################################################################
# Match
########################################################################################################################


@dataclass(frozen=True, order=True)
class Match(Rule):
    """When an item is validated by the ``validator``, the action will be done"""

    group: Group
    action: str = ""

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        yield self, Empty(valid=True)
        yield Match(~self.group, EXCLUDE), Empty(valid=False)

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return self.group.alphabet

    @property
    def skipable(self) -> bool:
        return False

    @property
    def terminal(self) -> bool:
        return False
