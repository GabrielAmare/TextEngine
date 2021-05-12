from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Tuple, Iterator, FrozenSet

from .constants import T_STATE, EXCLUDE, ACTION
from .base import Rule, Match, Empty, Item, Group
from .generic_items import GenericItem, GenericItemSet

__all__ = ("Branch", "BranchSet")


########################################################################################################################
# Branch
########################################################################################################################

@dataclass(frozen=True, order=True)
class Branch(GenericItem):
    name: str
    rule: Rule
    priority: int = 0
    transfer: bool = False

    @property
    def as_group(self) -> BranchSet:
        return BranchSet(frozenset({self}))

    def new_rule(self, rule: Rule) -> Branch:
        return replace(self, rule=rule)

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for first, after in self.rule.splited:
            yield first, after

        if self.rule.skipable:
            yield Match(group=Group.always(), action=EXCLUDE), Empty(valid=True)

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return self.rule.alphabet

    @property
    def terminal(self) -> bool:
        return self.rule.terminal

    @property
    def is_valid(self) -> bool:
        return self.rule.is_valid

    @property
    def is_error(self) -> bool:
        return self.rule.is_error


class BranchSet(GenericItemSet[Branch]):
    @property
    def alphabet(self) -> FrozenSet[Item]:
        return frozenset({item for branch in self.items for item in branch.alphabet})

    @property
    def terminal(self) -> bool:
        return all(branch.terminal for branch in self.items)

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

    def append(self, other: Branch) -> BranchSet:
        return self + other

    def extend(self, other: BranchSet) -> BranchSet:
        return self | other
