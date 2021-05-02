from dataclasses import dataclass
from typing import Tuple, Iterator, FrozenSet

from .items import Item, ALWAYS
from .rules import Rule, Valid, Error, Match, IGNORE

__all__ = ("Branch", "BranchSet")


########################################################################################################################
# Branch
########################################################################################################################

@dataclass(frozen=True, order=True)
class Branch:
    name: str
    rule: Rule
    priority: int = 0
    transfer: bool = False

    def __or__(self, other):
        if isinstance(other, Branch):
            return self.__class__(frozenset({self, other}))
        elif isinstance(other, BranchSet):
            return self.__class__(frozenset({self, *other.branches}))
        else:
            raise TypeError(type(other))

    __ior__ = __or__

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
            yield Match(group=ALWAYS, action=IGNORE), Valid()

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


@dataclass(frozen=True, order=True)
class BranchSet:
    branches: FrozenSet[Branch]

    def __or__(self, other):
        if isinstance(other, Branch):
            return self.__class__(frozenset({*self.branches, other}))
        elif isinstance(other, BranchSet):
            return self.__class__(frozenset({*self.branches, *other.branches}))
        else:
            raise TypeError(type(other))

    __ior__ = __or__

    @property
    def alphabet(self) -> FrozenSet[Item]:
        return frozenset({item for branch in self.branches for item in branch.alphabet})

    @property
    def terminal(self) -> bool:
        return all(branch.terminal for branch in self.branches)

    def terminal_code(self, throw_errors: bool = False) -> Iterator[str]:
        valid_branches = [branch for branch in self.branches if branch.is_valid]
        valid_max_priority = max([branch.priority for branch in valid_branches], default=0)
        valid_names = [branch.name for branch in valid_branches if branch.priority == valid_max_priority]

        if valid_names:
            return valid_names

        error_branches = [branch for branch in self.branches if branch.is_error]
        error_max_priority = max([branch.priority for branch in error_branches], default=0)
        error_names = [branch.name for branch in error_branches if branch.priority == error_max_priority]

        if error_names:
            if throw_errors:
                return []
            else:
                if error_names:
                    return ["!" + "|".join(error_names)]
                else:
                    return ["!"]
