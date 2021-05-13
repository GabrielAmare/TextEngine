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
    def atbs(self) -> PickAction:
        atbs: PickAction = PickAction()
        for atb in self.items:
            atbs.add(atb.action, atb.branch)
        return atbs


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


class PickAction(Dict[ACTION, BranchSet]):
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


class PickGroup(Dict[Group, PickAction]):
    @staticmethod
    def from_gto(gto: GroupToOutcome) -> PickGroup:
        return PickGroup({
            group: outcome.atbs
            for group, outcome in gto.items()
        })

    @property
    def branch_sets(self) -> Iterator[BranchSet]:
        for atbs in self.values():
            for branch_set in atbs.values():
                yield branch_set

    @property
    def cases(self) -> Iterator[Tuple[Group, PickAction]]:
        for group, atbs in self.items():
            if not group.inverted:
                yield group, atbs

    @property
    def default(self) -> PickAction:
        for group, atbs in self.items():
            if group.inverted:
                return atbs
        return PickAction()

    def l2s(self, func: FUNC, formal: bool = False) -> Iterator[L2]:
        for group, atbs in self.cases:
            yield L2(group=group, l1=atbs.l1(func, formal))

    def l3(self, func: FUNC, formal: bool = False) -> L3:
        return L3(cases=list(self.l2s(func)), default=self.default.l1(func, formal))


class PickBranchSet(Dict[BranchSet, PickGroup]):
    def l4s(self, func: FUNC, formal: bool = False) -> Iterator[L4]:
        for origin, gtatbs in self.items():
            yield L4(value=func(origin), switch=gtatbs.l3(func, formal))

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
        self.pbs: PickBranchSet = PickBranchSet()
        self.reflexive: bool = reflexive
        self.formal: bool = formal
        self.skips: List[T_STATE] = skips

        self.branch_sets: List[BranchSet] = [self.branch_set]

        self.build()

    def build(self) -> None:
        """
            This will iteratively build the cases of the parser
            from the original branchset to all the possible consequent branchsets
        """
        index = 0
        while index < len(self.branch_sets):
            branch_set: BranchSet = self.branch_sets[index]
            gtatbs: PickGroup = self.extract(branch_set)
            self.pbs[branch_set] = gtatbs
            self.include(gtatbs)
            index += 1

    def include(self, gtatbs: PickGroup) -> None:
        for branch_set in gtatbs.branch_sets:
            if branch_set.is_terminal:
                continue

            if branch_set in self.branch_sets:
                continue

            self.branch_sets.append(branch_set)

    def extract(self, branch_set: BranchSet) -> PickGroup:
        gto: GroupToOutcome = GroupToOutcome.from_branch_set(branch_set).optimized
        gtatbs: PickGroup = PickGroup.from_gto(gto)
        return gtatbs

    def get_nt_state(self, branch_set: BranchSet) -> NT_STATE:
        return NT_STATE(self.branch_sets.index(branch_set))

    @property
    def l6(self) -> L6:
        return L6(name=self.name, l5=self.pbs.l5(self.get_nt_state, self.formal))

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
