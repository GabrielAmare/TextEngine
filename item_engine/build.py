from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Iterator, Tuple, Optional, Type

import python_generator as pg

from .generic_items import GenericItem, GenericItemSet, optimized
from .constants import ACTION, STATE, NT_STATE, T_STATE
from .base import Group, BranchSet, Branch, Element

from tools37 import CsvFile
from graph37 import Node
from .BuilderGraph import BuilderGraph

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


@dataclass
class TargetSelect:
    non_terminal_part: BranchSet = field(default_factory=BranchSet)
    valid_branches: List[Branch] = field(default_factory=list)
    error_branches: List[Branch] = field(default_factory=list)
    valid_priority: int = 0
    error_priority: int = 0

    @property
    def target(self) -> BranchSet:
        return self.non_terminal_part | BranchSet(self.valid_branches)

    @property
    def priority(self):
        if self.non_terminal_part:
            return 2, 1
        elif self.valid_branches:
            return 1, self.valid_priority
        else:
            return 0, self.error_priority

    def add_branch(self, branch: Branch) -> None:
        if not branch.is_terminal:
            self.non_terminal_part += branch
        elif branch.is_valid:
            if branch.priority > self.valid_priority:
                self.valid_priority = branch.priority
                self.valid_branches = [branch]
            elif branch.priority == self.valid_priority:
                self.valid_branches.append(branch)
        elif branch.is_error:
            if branch.priority > self.error_priority:
                self.error_priority = branch.priority
                self.error_branches = [branch]
            elif branch.priority == self.error_priority:
                self.error_branches.append(branch)
        else:
            raise Exception(f"Unknown case for branch neither non-terminal, valid or error !")

    def get_target_states(self, func: FUNC) -> Iterator[STATE]:
        if self.non_terminal_part:
            return [func(self.target)]
        elif self.valid_branches:
            return [T_STATE(branch.name) for branch in self.valid_branches]
        elif self.error_branches:
            return [T_STATE("!" + "|".join(sorted(branch.name for branch in self.error_branches)))]
        else:
            return [T_STATE("!")]


class ActionSelect(Dict[ACTION, TargetSelect]):
    def add(self, action: ACTION, branch: Branch) -> None:
        if action in self:
            target_select = self[action]
        else:
            self[action] = target_select = TargetSelect()
        target_select.add_branch(branch)

    def code(self, func: FUNC, formal: bool = False) -> pg.LINES:
        max_priority = max(target_select.priority for target_select in self.values())
        cases = [
            pg.YIELD(line=f"{action!r}, {value!r}")
            for action, target_select in self.items()
            if target_select.priority == max_priority
            for value in target_select.get_target_states(func)
        ]

        if formal and len(cases) != 1:
            raise AmbiguityException(cases)

        if len(cases) == 0:
            return pg.PASS

        return pg.LINES(lines=cases)

    @property
    def targets(self) -> Iterator[BranchSet]:
        """Return all the non-terminal branch-sets"""
        for target_select in self.values():
            if target_select.non_terminal_part:
                yield target_select.target


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
            yield from action_select.targets

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

    def code(self, func: FUNC, formal: bool = False) -> pg.SWITCH:
        cases = sorted(self.cases, key=lambda item: len(item[0].items))
        return pg.SWITCH(
            ifs=[
                pg.IF(
                    cond=group.condition,
                    body=action_select.code(func, formal)
                )
                for group, action_select in cases
            ],
            default=self.default.code(func, formal) if self.default else None
        )


class OriginSelect(Dict[BranchSet, GroupSelect]):
    def code(self, func: FUNC, formal: bool = False) -> pg.SWITCH:
        return pg.SWITCH(
            ifs=[
                pg.IF(
                    cond=pg.EQ("value", repr(func(origin))),
                    body=group_select.code(func, formal)
                )
                for origin, group_select in self.items()
            ],
            default=pg.RAISE(pg.EXCEPTION("f'\\nvalue: {value!r}\\nitem: {item!r}'"))
        )


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
        self.origin_select: OriginSelect = OriginSelect()

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
            self.origin_select[branch_set] = group_select
            self.include(group_select)
            index += 1

    def include(self, group_select: GroupSelect) -> None:
        for branch_set in group_select.targets:
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
    def code(self) -> pg.MODULE:
        return pg.MODULE(items=[
            pg.FROM_IMPORT("typing", pg.ARGS("Iterator", "Tuple")),
            pg.FROM_IMPORT("item_engine", pg.ARGS("NT_STATE", "Element", "ACTION", "STATE")),
            pg.SETATTR(k="__all__", v=pg.LIST([pg.STR(self.name)])),
            pg.DEF(
                name=self.name,
                args=pg.ARGS("value: NT_STATE", "item: Element"),
                body=self.origin_select.code(self.get_nt_state, self.formal),
                type="Iterator[Tuple[ACTION, STATE]]"
            ),
        ])

    def to_csv(self, fp: str) -> None:
        data = []

        for origin, group_select in self.origin_select.items():
            for group, action_select in (*group_select.cases, (Group.never(), group_select.default)):
                for action, target_select in action_select.items():
                    for target_state in target_select.get_target_states(self.get_nt_state):
                        data.append(dict(
                            origin=str(self.get_nt_state(origin)),
                            group=str(group).replace('\n', ''),
                            action=action,
                            target=target_state
                        ))

        CsvFile.save(fp, keys=["origin", "group", "action", "target"], data=data)

    @property
    def graph(self, **config):
        dag = BuilderGraph(**config, name=self.name)

        branch_set_nodes: Dict[STATE, Node] = {}
        errors: Dict[T_STATE, Node] = {}
        valids: Dict[T_STATE, Node] = {}

        def get_branch_set_node(value: STATE):
            if isinstance(value, T_STATE):
                if value.startswith('!'):
                    value = '!' + '|'.join(sorted(value[1:].split('|')))
                    if value not in errors:
                        errors[value] = dag.terminal_error_state(value)
                    return errors[value]
                else:
                    if value not in valids:
                        valids[value] = dag.terminal_valid_state(value)
                    return valids[value]
            elif isinstance(value, NT_STATE):
                if value not in branch_set_nodes:
                    branch_set_nodes[value] = dag.non_terminal_state(value)
                return branch_set_nodes[value]
            else:
                raise TypeError(type(value))

        memory = {}

        def make_chain(origin: NT_STATE, group: Group, action: ACTION, target: STATE):
            origin_node = get_branch_set_node(origin)
            target_node = get_branch_set_node(target)
            k1 = (group, action, target_node)
            if k1 in memory:
                group_action_node = memory[k1]
            else:
                memory[k1] = group_action_node = dag.group_action(group, action)
                dag.link(group_action_node, target_node)

            k3 = (origin_node, group_action_node)
            if k3 not in memory:
                memory[k3] = dag.link(origin_node, group_action_node)

        for origin, group_select in self.origin_select.items():
            origin_value = self.get_nt_state(origin)
            for group, action_select in group_select.cases:
                for action, target_select in action_select.items():
                    target_states = target_select.get_target_states(self.get_nt_state)
                    target_states = sorted(target_states, key=lambda state: not isinstance(state, str))
                    for target_value in target_states:
                        make_chain(origin_value, group, action, target_value)

        return dag


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

        import_section = pg.IMPORT_SECTION()
        import_section.append("typing", "Iterator")
        import_section.append("item_engine", pg.IMPORT_ALL)

        for parser in self.parsers:
            import_section.append(parser.input_cls.__module__, parser.input_cls.__name__)
            import_section.append(parser.output_cls.__module__, parser.output_cls.__name__)
            import_section.append("." + parser.name, parser.name)

        return pg.PACKAGE(name=self.name, modules={
            '__init__': pg.MODULE(items=[
                import_section,
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
                                    pg.ARG("input_cls", v=parser.input_cls.__name__),
                                    pg.ARG("output_cls", v=parser.output_cls.__name__),
                                    pg.ARG("to_ignore", v=repr(parser.skips)),
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
