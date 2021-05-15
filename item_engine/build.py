from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Callable, Iterator, Tuple, Optional, Type
import python_generator as pg

from .generate import L0, L1, L2, L3, L4, L5, L6
from .generic_items import GenericItem, GenericItemSet, optimized
from .constants import ACTION, STATE, NT_STATE, T_STATE
from .base import Group, BranchSet, Branch, Element

__all__ = ["Parser", "Engine"]


class AmbiguityException(Exception):
    pass


@dataclass(frozen=True, order=True)
class ActionToBranch(GenericItem):
    action: ACTION
    branch: Branch

    @property
    def as_group(self) -> Outcome:
        return Outcome({self})


class Outcome(GenericItemSet[ActionToBranch]):
    @property
    def action_select(self) -> ActionSelect:
        action_select: ActionSelect = ActionSelect()
        for atb in self.items:
            action_select.add(atb.action, atb.branch)
        return action_select


class GroupToOutcome(Dict[Group, Outcome]):
    @classmethod
    def from_branch_set(cls, branch_set: BranchSet) -> GroupToOutcome:
        self: GroupToOutcome = cls()
        for branch in branch_set.items:
            for first, after in branch.splited:
                self.add(first.group, first.action, branch.new_rule(after))
        return self

    @property
    def optimized(self) -> GroupToOutcome:
        return GroupToOutcome(optimized(self))

    def add(self, group: Group, action: ACTION, branch: Branch) -> None:
        atb = ActionToBranch(action, branch)
        if group in self:
            self[group] |= atb.as_group
        else:
            self[group] = atb.as_group


FUNC = Callable[[BranchSet], STATE]


class ActionSelect(Dict[ACTION, BranchSet]):
    def add(self, action: ACTION, branch: Branch) -> None:
        if action in self:
            self[action] |= branch.as_group
        else:
            self[action] = branch.as_group

    def l0s(self, func: FUNC, throw_errors: bool) -> Iterator[L0]:
        for action, branch_set in self.items():
            if branch_set.is_terminal:
                for value in branch_set.terminal_code(throw_errors):
                    yield L0(action=action, value=value)
            else:
                yield L0(action=action, value=func(branch_set))

    def l1(self, func: FUNC, formal: bool = False) -> L1:
        # we throw errors when there's something different than an error
        throw_errors = not all(branch.is_error for branch_set in self.values() for branch in branch_set.items)

        cases = list(self.l0s(func, throw_errors))

        if formal and len(cases) != 1:
            raise AmbiguityException()

        return L1(cases=cases)


class GroupSelect(Dict[Group, ActionSelect]):
    @staticmethod
    def from_gto(gto: GroupToOutcome) -> GroupSelect:
        return GroupSelect({
            group: outcome.action_select
            for group, outcome in gto.items()
        })

    @property
    def targets(self) -> Iterator[BranchSet]:
        for action_select in self.values():
            for target in action_select.values():
                yield target

    @property
    def cases(self) -> Iterator[Tuple[Group, ActionSelect]]:
        for group, action_select in self.items():
            if not group.inverted:
                yield group, action_select

    @property
    def default(self) -> ActionSelect:
        # TODO : check if no default means that all items are handled by the cases,
        #  in this case : an optimization could be to take the more time-consuming case as default
        #  (and therefore not having to verify it)
        for group, action_select in self.items():
            if group.inverted:
                return action_select
        return ActionSelect()

    def l2s(self, func: FUNC, formal: bool = False) -> Iterator[L2]:
        for group, action_select in self.cases:
            yield L2(group=group, l1=action_select.l1(func, formal))

    def l3(self, func: FUNC, formal: bool = False) -> L3:
        return L3(cases=list(self.l2s(func)), default=self.default.l1(func, formal))


class ValueSelect(Dict[BranchSet, GroupSelect]):
    def l4s(self, func: FUNC, formal: bool = False) -> Iterator[L4]:
        for origin, group_select in self.items():
            yield L4(value=func(origin), switch=group_select.l3(func, formal))

    def l5(self, func: FUNC, formal: bool = False) -> L5:
        return L5(cases=list(self.l4s(func, formal)))


class Parser:
    def __init__(self,
                 name: str,
                 branch_set: BranchSet,
                 input_cls: Type[Element],
                 output_cls: Type[Element],
                 skips: List[T_STATE],
                 reflexive: bool,
                 formal: bool,
                 ):
        """

        :param name: The name of the parser, it will be used to name the module
        :param branch_set: The BranchSet including all the patterns defined in the parser grammar
        :param input_cls: The type of elements the parser will receive
        :param output_cls: The type of elements the parser will emit
        :param skips: The list of element types that must be ignored (commonly used for white space patterns)
        :param reflexive: Will the parser receive what it emits (used to build recursive grammar)
        :param formal: Is the parser formal ? If it's the case, any ambiguity will raise a SyntaxError
        """
        self.name: str = name
        self.branch_set: BranchSet = branch_set
        self.input_cls: Type[Element] = input_cls
        self.output_cls: Type[Element] = output_cls
        self.reflexive: bool = reflexive
        self.formal: bool = formal
        self.skips: List[T_STATE] = skips

        self.branch_sets: List[BranchSet] = [self.branch_set]
        self.value_select: ValueSelect = ValueSelect()

        self.build()

    def build(self) -> None:
        """
            This will iteratively build the cases of the parser
            from the original branchset to all the possible consequent branchsets
        """
        index = 0
        while index < len(self.branch_sets):
            branch_set: BranchSet = self.branch_sets[index]
            group_select: GroupSelect = self.extract(branch_set)
            self.value_select[branch_set] = group_select
            self.include(group_select)
            index += 1

    def include(self, gtatbs: GroupSelect) -> None:
        for branch_set in gtatbs.targets:
            if branch_set.is_terminal:
                continue

            if branch_set in self.branch_sets:
                continue

            self.branch_sets.append(branch_set)

    def extract(self, branch_set: BranchSet) -> GroupSelect:
        gto: GroupToOutcome = GroupToOutcome.from_branch_set(branch_set).optimized
        group_select: GroupSelect = GroupSelect.from_gto(gto)
        return group_select

    def get_nt_state(self, branch_set: BranchSet) -> NT_STATE:
        return NT_STATE(self.branch_sets.index(branch_set))

    @property
    def l6(self) -> L6:
        return L6(name=self.name, l5=self.value_select.l5(self.get_nt_state, self.formal))

    @property
    def code(self) -> pg.MODULE:
        """Generate a CODE object which represent the parser"""
        return self.l6.code


class Engine:
    def __init__(self,
                 name: str,
                 parsers: List[Parser],
                 operators: Optional[pg.MODULE] = None
                 ):
        assert name.isidentifier()
        assert not any(parser.name == 'operators' for parser in parsers)
        self.name: str = name
        self.parsers: List[Parser] = parsers
        self.operators: Optional[pg.MODULE] = operators

    @property
    def code(self) -> pg.PACKAGE:
        """

        def gen_networks(lexer_cfg):
            yield Network(parser=lexer, **lexer_cfg)
            yield ReflexiveNetwork(parser=parser, **lexer_cfg)

        """
        return pg.PACKAGE(name=self.name, modules={
            '__init__': pg.MODULE(items=[
                pg.FROM_IMPORT("typing", pg.ARGS("Iterator")),
                pg.FROM_IMPORT("item_engine", pg.ARGS("*")),
                *[pg.FROM_IMPORT('.' + parser.name, pg.ARGS(parser.name)) for parser in self.parsers],
                pg.SETATTR("__all__", pg.LIST([pg.STR("gen_networks")])),
                pg.DEF(
                    name="gen_networks",
                    args=pg.ARGS(*[pg.ARG(f"{parser.name}_cfg", t="dict") for parser in self.parsers]),
                    type="Iterator[Network]",
                    body=pg.LINES([
                        pg.YIELD(
                            pg.CALL(
                                name="ReflexiveNetwork" if parser.reflexive else "Network",
                                args=pg.ARGS(
                                    pg.ARG("function", v=parser.name),
                                    pg.AS_KWARG(f"{parser.name}_cfg")
                                )
                            )
                        )
                        for parser in self.parsers
                    ])
                )
            ]),
            **({} if self.operators is None else {'materials': self.operators}),
            **{parser.name: parser.code for parser in self.parsers}
        })

    def build(self, root: str = os.curdir, allow_overwrite: bool = False) -> None:
        self.code.save(root=root, allow_overwrite=allow_overwrite)
