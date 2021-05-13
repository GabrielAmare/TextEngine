from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Tuple, Iterator, FrozenSet, List, TypeVar, Generic, Type
from functools import reduce
from operator import and_

from .constants import ACTION, INCLUDE, EXCLUDE, AS, IN, T_STATE
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


class HasAlphabet:
    @property
    def alphabet(self) -> FrozenSet[Item]:
        """
            Return a frozenset containing all the explicit items of a given rule
            It is possible that an item matches a rule without being in it's alphabet,
            this case occurs when the rule contains at some level a Match which has an inverted Group.
        """
        if isinstance(self, Empty):
            return frozenset()
        elif isinstance(self, (RuleUnit, Branch)):
            return self.rule.alphabet
        elif isinstance(self, RuleList):
            return frozenset({item for rule in self.rules for item in rule.alphabet})
        elif isinstance(self, Match):
            return self.group.items
        elif isinstance(self, BranchSet):
            return frozenset({item for branch in self.items for item in branch.alphabet})
        else:
            raise TypeError(type(self))


class HasState:
    @property
    def is_valid(self) -> bool:
        """Return True when a Rule is valid"""
        if isinstance(self, Empty):
            return self.valid
        elif isinstance(self, All):
            return len(self.rules) == 1 and self.rules[0].is_valid
        elif isinstance(self, Any):
            return all(rule.is_valid for rule in self.rules)
        elif isinstance(self, Branch):
            return self.rule.is_valid
        else:
            return False

    @property
    def is_error(self) -> bool:
        """Return True when a Rule is error"""
        if isinstance(self, Empty):
            return not self.valid
        elif isinstance(self, All):
            return len(self.rules) == 1 and self.rules[0].is_error
        elif isinstance(self, Any):
            return all(rule.is_error for rule in self.rules)
        elif isinstance(self, Branch):
            return self.rule.is_error
        else:
            return False

    @property
    def is_terminal(self) -> bool:
        """Return True when a Rule is terminal"""
        if isinstance(self, Empty):
            return True
        elif isinstance(self, All):
            return len(self.rules) == 1 and self.rules[0].is_terminal
        elif isinstance(self, Any):
            return all(rule.is_terminal for rule in self.rules)
        elif isinstance(self, Branch):
            return self.rule.is_terminal
        elif isinstance(self, BranchSet):
            return all(branch.is_terminal for branch in self.items)
        else:
            return False


class CanBeSplited:
    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        """
            Split the rules by returning a Match followed by the remaining Rule after the Match
        """
        if isinstance(self, Empty):
            if self.is_valid:
                yield Match(group=Group.always(), action=EXCLUDE), self
            else:
                yield Match(group=Group.never(), action=EXCLUDE), self
        elif isinstance(self, Optional):
            for first, after in self.rule.splited:
                yield first, after
        elif isinstance(self, Repeat):
            for first, after in self.rule.splited:
                yield first, after & self
        elif isinstance(self, All):
            for rule_first, rule_after in self.decompose:
                for first, after in rule_first.splited:
                    yield first, after & rule_after
        elif isinstance(self, Any):
            for rule in self.rules:
                for first, after in rule.splited:
                    yield first, after
        elif isinstance(self, Match):
            yield self, Empty(valid=True)
            yield Match(~self.group, EXCLUDE), Empty(valid=False)
        elif isinstance(self, Branch):
            for first, after in self.rule.splited:
                yield first, after

            if self.rule.is_skipable:
                yield Match(group=Group.always(), action=EXCLUDE), Empty(valid=True)
        else:
            raise ValueError(self)


########################################################################################################################
# Rule
########################################################################################################################

@dataclass(frozen=True, order=True)
class Rule(HasAlphabet, HasState, CanBeSplited):
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

    @property
    def is_skipable(self: Rule) -> bool:
        """Return True when a Rule is skipable"""
        if isinstance(self, (Optional, Repeat)):
            return True
        elif isinstance(self, All):
            return all(rule.is_skipable for rule in self.rules)
        elif isinstance(self, Any):
            return any(rule.is_skipable for rule in self.rules)
        else:
            return False


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
    @property
    def decompose(self) -> Iterator[Tuple[Rule, Rule]]:
        for index, rule in enumerate(self.rules):
            if index + 1 < len(self.rules):
                yield rule, reduce(and_, self.rules[1:])
            else:
                yield rule, Empty(valid=True)

            if not rule.is_skipable:
                break


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


__all__ += ["Branch", "BranchSet"]


########################################################################################################################
# Branch
########################################################################################################################

@dataclass(frozen=True, order=True)
class Branch(GenericItem, HasAlphabet, HasState, CanBeSplited):
    name: str
    rule: Rule
    priority: int = 0
    transfer: bool = False

    @property
    def as_group(self) -> BranchSet:
        return BranchSet(frozenset({self}))

    def new_rule(self, rule: Rule) -> Branch:
        return replace(self, rule=rule)


class BranchSet(GenericItemSet[Branch], HasAlphabet, HasState):
    def terminal_code(self, throw_errors: bool = False) -> Iterator[T_STATE]:
        valid_branches = [branch for branch in self.items if branch.is_valid]
        valid_max_priority = max([branch.priority for branch in valid_branches], default=0)
        valid_names = [T_STATE(branch.name) for branch in valid_branches if branch.priority == valid_max_priority]

        if valid_names:
            return valid_names

        error_branches = [branch for branch in self.items if branch.is_error]
        error_max_priority = max([branch.priority for branch in error_branches], default=0)
        error_names = [branch.name for branch in error_branches if branch.priority == error_max_priority]

        if error_names:
            if throw_errors:
                return []
            else:
                if error_names:
                    return [T_STATE("!" + "|".join(error_names))]
                else:
                    return [T_STATE("!")]

    def get_all_cases(self) -> Iterator[Tuple[Group, ACTION, Branch]]:
        for branch in self.items:
            for first, after in branch.splited:
                yield first.group, first.action, branch.new_rule(after)

    @property
    def only_non_terminals(self) -> BranchSet:
        """Remove the terminal branches"""
        return BranchSet(frozenset(branch for branch in self.items if not branch.is_terminal))

    @property
    def only_valids(self) -> BranchSet:
        """Remove the terminal branches"""
        return BranchSet(frozenset(branch for branch in self.items if branch.is_valid))

    @property
    def only_errors(self) -> BranchSet:
        """Remove the terminal branches"""
        return BranchSet(frozenset(branch for branch in self.items if branch.is_error))
