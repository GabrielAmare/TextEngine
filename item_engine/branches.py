from __future__ import annotations
from typing import Tuple, Iterator, FrozenSet

from .constants import T_STATE, EXCLUDE
from .items import Item, Group
from .rules import Rule, Valid, Error, Match
from .generic_items import Item as __Item__, ItemSet as __ItemSet__

__all__ = ("Branch", "BranchSet")


########################################################################################################################
# Branch
########################################################################################################################

class Branch(__Item__):
    @property
    def as_group(self) -> BranchSet:
        return BranchSet(frozenset({self}))

    def __init__(self, name: str, rule: Rule, priority: int = 0, transfer: bool = False):
        self.name: str = name
        self.rule: Rule = rule
        self.priority: int = priority
        self.transfer: bool = transfer

    def __eq__(self, other: Branch):
        return self.name == other.name and \
               self.rule == other.rule and \
               self.priority == other.priority and \
               self.transfer == other.transfer

    def __hash__(self):
        return hash((type(self), self.name, self.rule, self.priority, self.transfer))

    def new_rule(self, rule: Rule):
        return Branch(
            name=self.name,
            rule=rule,
            priority=self.priority,
            transfer=self.transfer
        )

    @property
    def splited(self) -> Iterator[Tuple[Match, Rule]]:
        for first, after in self.rule.splited:
            yield first, after

        if self.rule.skipable:
            yield Match(group=Group.always(), action=EXCLUDE), Valid()

    @property
    def alphabet(self):
        return self.rule.alphabet

    @property
    def terminal(self) -> bool:
        return self.rule.terminal

    @property
    def is_valid(self) -> bool:
        return isinstance(self.rule, Valid)

    @property
    def is_error(self) -> bool:
        return isinstance(self.rule, Error)


class BranchSet(__ItemSet__[Branch]):
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
