from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Union, Tuple, FrozenSet, Iterator, Generic, TypeVar, Deque, Type

import python_generator as pg

from .items import *
from .branches import *
from .generate import *

__all__ = ["Parser", "make_module"]


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

    def _ast(self, get_bs_code, throw_errors) -> Iterator[L0]:
        for action, branch_set in self:
            if branch_set.terminal:
                for value in branch_set.terminal_code(throw_errors):
                    yield L0(action=action, value=value)
            else:
                yield L0(action=action, value=get_bs_code(branch_set))

    def ast(self, get_bs_code) -> L1:
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
            if group != ALWAYS:
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


K = TypeVar("K")


class Pile(Generic[K]):
    def __init__(self, *data: K):
        self.data: Deque[K] = deque(data)
        self.length = len(data)

    def __contains__(self, item: K) -> bool:
        return item in self.data

    def __iter__(self) -> Iterator[K]:
        while self.length > 0:
            yield self.data.popleft()
            self.length -= 1

    def append(self, item: K) -> None:
        self.length += 1
        self.data.append(item)


class Parser:
    def __init__(self, name: str, lexer: BranchSet, group_cls: type):
        self.name = name

        base_items: FrozenSet[Item] = lexer.alphabet

        self.group_any_other = group_cls(base_items, False)

        self.branch_sets: List[BranchSet] = []
        todo: Pile[BranchSet] = Pile(lexer)

        self.value_cases: List[ValueCase] = []

        for branch_set in todo:
            self.branch_sets.append(branch_set)

            flattened: Flattened = Flattened(branch_set)

            group_cases: GroupCases = GroupCases.make(
                items=sorted(base_items) + [AnyOther()],
                flattened=flattened,
                group_cls=group_cls
            )

            default: ActionToBranchSet = group_cases.pop_default()

            always: ActionToBranchSet = ActionToBranchSet()
            for action, group, branch in flattened:
                if group == ALWAYS:
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

    @property
    def code(self) -> pg.DEF:
        """Generate a CODE object which represent the parser"""
        return L6(
            name=self.name,
            l5=L5(
                cases=[
                    L4(
                        value=self.branch_sets.index(value_case.origin),
                        switch=L3(
                            cases=[
                                L2(group=group, l1=atbs.ast(self.branch_sets.index))
                                for group, atbs in value_case
                            ],
                            default=value_case.default.ast(self.branch_sets.index)
                        ),
                        always=value_case.always.ast(self.branch_sets.index)
                    )
                    for value_case in self.value_cases
                ]
            )
        ).code


def make_module(fp: str, *data: Tuple[str, BranchSet, Type[Group]], overwrite: bool = False):
    return pg.MODULE([
        pg.FROM_IMPORT("typing", pg.ARGS("Iterator", "Tuple", "Union")),
        *(
            Parser(name=name, lexer=lexer, group_cls=group_cls).code
            for name, lexer, group_cls in data
        )
    ]).save(fp, overwrite=overwrite)
