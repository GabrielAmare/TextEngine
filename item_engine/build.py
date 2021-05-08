from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import List, Dict, Union, Tuple, FrozenSet, Iterator, Optional, Callable

import python_generator as pg

from .utils import *
from .items import *
from .branches import *
from .generate import *
from .constants import NT_STATE, STATE

__all__ = ["Parser", "Engine", ]


@dataclass
class ActionToBranchSet:
    data: Dict[str, BranchSet] = field(default_factory=dict)

    def __iter__(self):
        return iter(self.data.items())

    def __hash__(self):
        return hash((type(self), frozenset(self.data.items())))

    def __bool__(self):
        return bool(self.data)

    def add(self, action: str, obj: Union[Branch, BranchSet]):
        if isinstance(obj, Branch):
            obj = BranchSet(frozenset({obj}))

        if action in self.data:
            self.data[action] |= obj
        else:
            self.data[action] = obj

    def __or__(self, other):
        assert isinstance(other, ActionToBranchSet)
        atbs = ActionToBranchSet()
        for action, branch_set in (*self, *other):
            atbs.add(action, branch_set)

        return atbs

    __ior__ = __or__

    def _ast(self, get_bs_code: Callable[[BranchSet], STATE], throw_errors: bool) -> Iterator[L0]:
        for action, branch_set in self:
            if branch_set.terminal:
                for value in branch_set.terminal_code(throw_errors):
                    yield L0(action=action, value=value)
            else:
                yield L0(action=action, value=get_bs_code(branch_set))

    def ast(self, get_bs_code: Callable[[BranchSet], STATE]) -> L1:
        throw_errors = not all(branch.is_error for branch_set in self.data.values() for branch in branch_set.branches)

        return L1(cases=list(self._ast(get_bs_code, throw_errors)))


@dataclass
class ActionCase:
    action: str
    branch_set: BranchSet


@dataclass
class ItemCase:
    group: Group
    atbs: ActionToBranchSet


@dataclass
class ValueSwitch:
    cases: List[ItemCase]
    default: ActionToBranchSet


@dataclass
class ValueCase:
    origin: BranchSet
    cases: Dict[Group, ActionToBranchSet]
    default: ActionToBranchSet
    always: ActionToBranchSet

    def __iter__(self) -> Iterator[Tuple[Group, ActionToBranchSet]]:
        for group, atbs in sorted(self.cases.items(), key=lambda pair: -sum(bs.terminal for act, bs in pair[1])):
            yield group, atbs


class ItemSigns:
    def __init__(self, items: List[Item], groups: List[Group]):
        self.items: List[Item] = items
        self.signs: List[str] = [
            ''.join('01'[item in group] for group in groups)
            for item in self.items
        ]

    def __iter__(self) -> Iterator[Tuple[Item, str]]:
        return iter(zip(self.items, self.signs))


class SignToGroup(Dict[str, Group]):
    def add(self, sign: str, group: Group):
        if sign in self:
            self[sign] |= group
        else:
            self[sign] = group

    @classmethod
    def make(cls, item_signs: ItemSigns, group_cls):
        self: cls = cls()
        for item, sign in item_signs:
            self.add(sign, group_cls(frozenset({item})))

        return self


class Flattened:
    def __init__(self, branch_set: BranchSet):
        self.actions: List[str] = []
        self.groups: List[Group] = []
        self.branches: List[Branch] = []
        self.data: List[Tuple[str, Group, Branch]] = []

        for branch in branch_set.branches:
            for first, after in branch.splited:
                self.actions.append(first.action)
                self.groups.append(first.group)
                self.branches.append(branch.new_rule(after))

    def __iter__(self) -> Iterator[Tuple[str, Group, Branch]]:
        return iter(zip(self.actions, self.groups, self.branches))


class ItemCases(Dict[Item, ActionToBranchSet]):
    def add(self, item: Item, action: str, branch: Branch):
        if item in self:
            self[item].add(action, branch)
        else:
            self[item] = ActionToBranchSet({action: BranchSet(frozenset({branch}))})

    @classmethod
    def make(cls, items: List[Item], flattened: Flattened):
        self: cls = cls()

        for action, group, branch in flattened:
            if not group.is_always:
                for item in items:
                    if item in group:
                        self.add(item, action, branch)

        return self


class GroupCases(Dict[Group, ActionToBranchSet]):
    def add(self, group: Group, atbs: ActionToBranchSet):
        if group in self:
            self[group] |= atbs
        else:
            self[group] = atbs

    @classmethod
    def make(cls, items: List[Item], flattened: Flattened, group_cls):
        item_cases: ItemCases = ItemCases.make(
            items=items,
            flattened=flattened
        )

        item_signs: ItemSigns = ItemSigns(
            items=items,
            groups=flattened.groups
        )

        s2g: SignToGroup = SignToGroup.make(
            item_signs=item_signs,
            group_cls=group_cls
        )

        self: cls = cls()
        for item, sign in item_signs:
            self.add(s2g[sign], item_cases[item])
        return self

    @property
    def non_terminal_branch_sets(self) -> Iterator[BranchSet]:
        for atbs in self.values():
            for branch_set in atbs.data.values():
                if not branch_set.terminal:
                    yield branch_set

    def pop_default(self) -> ActionToBranchSet:
        for group in self.keys():
            if AnyOther() in group:
                return self.pop(group)
        else:
            return ActionToBranchSet()


class Parser:
    def __init__(self, name: str, branch_set: BranchSet, group_cls: type, reflexive: bool = False,
                 show_progress: bool = True):
        self.name = name
        self.reflexive = reflexive

        base_items: FrozenSet[Item] = branch_set.alphabet

        self.group_any_other = group_cls(base_items, False)

        self.branch_sets: List[BranchSet] = []
        todo: Pile[BranchSet] = Pile(branch_set)

        self.value_cases: List[ValueCase] = []

        for branch_set in todo:
            self.branch_sets.append(branch_set)
            if show_progress:
                print(f'handling case n°{self.branch_sets.index(branch_set)}')

            flattened: Flattened = Flattened(branch_set)

            group_cases: GroupCases = GroupCases.make(
                items=sorted(base_items) + [AnyOther()],
                flattened=flattened,
                group_cls=group_cls
            )

            default: ActionToBranchSet = group_cases.pop_default()

            always: ActionToBranchSet = ActionToBranchSet()
            for action, group, branch in flattened:
                if group.is_always:
                    default.add(action, branch)
                    # always.add(action, branch)

            self.value_cases.append(
                ValueCase(
                    origin=branch_set,
                    cases=group_cases,
                    default=default,
                    always=always
                )
            )

            for bs in group_cases.non_terminal_branch_sets:
                if bs not in self.branch_sets:
                    if bs not in todo:
                        todo.append(bs)
                        # print(repr(bs))

        if show_progress:
            print('all cases handled !')

    def get_nt_state(self, branch_set: BranchSet) -> NT_STATE:
        return NT_STATE(self.branch_sets.index(branch_set))

    @property
    def l6(self):
        return L6(
            name=self.name,
            l5=L5(
                cases=[
                    L4(
                        value=self.get_nt_state(value_case.origin),
                        switch=L3(
                            cases=[
                                L2(group=group, l1=atbs.ast(self.get_nt_state))
                                for group, atbs in value_case
                            ],
                            default=value_case.default.ast(self.get_nt_state)
                        ),
                        always=value_case.always.ast(self.get_nt_state)
                    )
                    for value_case in self.value_cases
                ]
            )
        )

    @property
    def code(self) -> pg.MODULE:
        """Generate a CODE object which represent the parser"""
        return self.l6.code


class Engine:
    def __init__(self, name: str, parsers: List[Parser], operators: Optional[pg.MODULE] = None):
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
