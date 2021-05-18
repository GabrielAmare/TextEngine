from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
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
        data = []
        for branch in branch_set.items:
            for first, after in branch.splited:
                data.append([str(branch), str(first.group), str(first.action), str(after)])
                self.add(first.group, first.action, branch.new_rule(after))

        from tools37 import ReprTable
        print(str(ReprTable(data)))

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


class ERROR_MODE(Enum):
    FULL = "FULL"
    MOST = "MOST"
    NONE = "NONE"


@dataclass
class TargetSelect:
    non_terminal_part: BranchSet = field(default_factory=BranchSet)
    valid_branches: List[Branch] = field(default_factory=list)
    error_branches: List[Branch] = field(default_factory=list)
    valid_priority: int = 0
    error_priority: int = 0

    @property
    def target(self) -> BranchSet:
        return self.non_terminal_part | BranchSet(self.valid_branches) | BranchSet(self.error_branches)

    @property
    def priority(self):
        if self.non_terminal_part:
            return 2, 1
        elif self.valid_branches:
            return 1, -self.valid_priority
        else:
            return 0, -self.error_priority

    def add_branch(self, branch: Branch) -> None:
        if not branch.is_terminal:
            self.non_terminal_part += branch
        elif branch.is_valid:
            # self.valid_branches.append(branch)
            if branch.priority > self.valid_priority:
                self.valid_priority = branch.priority
                self.valid_branches = [branch]
            elif branch.priority == self.valid_priority:
                self.valid_branches.append(branch)
        elif branch.is_error:
            # self.error_branches.append(branch)
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

    def _data_valid(self) -> T_STATE:
        # if len(self.valid_branches) > 1:
        #     print(self.valid_branches)
        max_priority = max(branch.priority for branch in self.valid_branches)
        valid_branches = [branch for branch in self.valid_branches if branch.priority == max_priority]
        if len(valid_branches) == 1:
            return T_STATE(valid_branches[0].name)
        else:
            raise AmbiguityException

    def _data_error(self, error_mode: ERROR_MODE) -> T_STATE:
        if error_mode == ERROR_MODE.FULL:
            error_branches = self.error_branches
        elif error_mode == ERROR_MODE.MOST:
            max_priority = max(branch.priority for branch in self.error_branches)
            error_branches = [branch for branch in self.error_branches if branch.priority == max_priority]
        elif error_mode == ERROR_MODE.NONE:
            error_branches = []
        else:
            raise ValueError(error_mode, "invalid error mode")
        return T_STATE("!" + "|".join(sorted(branch.name for branch in error_branches)))

    def data(self, func: FUNC, error_mode: ERROR_MODE = ERROR_MODE.MOST) -> STATE:
        if self.non_terminal_part:  # priority given to non-terminal branches
            return func(self.target)
        elif self.valid_branches:  # then priority to valid branch with most priority
            return self._data_valid()
        elif self.error_branches:
            return self._data_error(error_mode)
        else:
            return T_STATE("!")


class ActionSelect(Dict[ACTION, TargetSelect]):
    def add(self, action: ACTION, branch: Branch) -> None:
        if action in self:
            target_select = self[action]
        else:
            self[action] = target_select = TargetSelect()
        target_select.add_branch(branch)

    def code(self, func: FUNC, formal: bool = False) -> pg.BLOCK:
        max_priority = max(target_select.priority for target_select in self.values())
        cases = [
            pg.ARGS(repr(action), repr(value)).YIELD()
            for action, target_select in self.items()
            if target_select.priority == max_priority
            for value in target_select.get_target_states(func)
        ]

        if formal and len(cases) != 1:
            raise AmbiguityException(cases)

        if len(cases) == 0:
            return pg.PASS

        return pg.BLOCK(*cases)

    @property
    def targets(self) -> Iterator[BranchSet]:
        """Return all the non-terminal branch-sets"""
        for target_select in self.values():
            if target_select.non_terminal_part:
                yield target_select.target

    def data(self, func: FUNC, formal: bool = False) -> ActionSelectData:
        max_priority = max(target_select.priority for target_select in self.values())
        cases = {
            action: target_select.data(func)
            for action, target_select in self.items()
            if target_select.priority == max_priority
        }

        if formal and len(cases) != 1:
            raise AmbiguityException(cases)

        return ActionSelectData(cases=cases)


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
            cases=[
                (group.condition(pg.VAR("item")), action_select.code(func, formal))
                for group, action_select in cases
            ],
            default=self.default.code(func, formal) if self.default else None
        )

    def data(self, func: FUNC, formal: bool = False) -> GroupSelectData:
        return GroupSelectData(
            {
                group: action_select.data(func, formal)
                for group, action_select
                in sorted(self.cases, key=lambda item: len(item[0].items))
            },
            self.default.data(func, formal)
        )


class OriginSelect(Dict[BranchSet, GroupSelect]):
    def code(self, func: FUNC, formal: bool = False) -> pg.SWITCH:
        return pg.SWITCH(
            cases=[
                (
                    pg.VAR("value").EQ(func(origin)),
                    group_select.code(func, formal)
                )
                for origin, group_select in self.items()
            ],
            default=pg.EXCEPTION("f'\\nvalue: {value!r}\\nitem: {item!r}'").RAISE()
        )

    def data(self, func: FUNC, formal: bool = False) -> OriginSelectData:
        return OriginSelectData(
            {
                func(origin): group_select.data(func, formal)
                for origin, group_select in self.items()
            }
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
        return pg.MODULE(
            self.name,
            [
                pg.IMPORT.FROM("typing", pg.ARGS("Iterator", "Tuple")),
                pg.IMPORT.FROM("item_engine", pg.ARGS("NT_STATE", "Element", "ACTION", "STATE")),
                pg.VAR("__all__").ASSIGN(pg.LIST([pg.STR(self.name)])),
                pg.DEF(
                    name=self.name,
                    args=pg.ARGS(pg.ARG("value", t="NT_STATE"), pg.ARG("item", t="Element")),
                    block=self.origin_select.code(self.get_nt_state, self.formal),
                    t="Iterator[Tuple[ACTION, STATE]]"
                ),
            ])

    def data(self) -> ParserData:
        return ParserData(
            name=self.name,
            input_cls=self.input_cls,
            output_cls=self.output_cls,
            formal=self.formal,
            osd=self.origin_select.data(self.get_nt_state, self.formal),

            reflexive=self.reflexive,
            skips=self.skips
        )

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
        return self.data().graph


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

        imports: List[pg.STATEMENT] = []
        for parser in self.parsers:
            imports.append(pg.IMPORT.FROM(parser.input_cls.__module__, parser.input_cls.__name__))
            imports.append(pg.IMPORT.FROM(parser.output_cls.__module__, parser.output_cls.__name__))
            imports.append(pg.IMPORT.FROM("." + parser.name, parser.name))

        return pg.PACKAGE(
            self.name,
            pg.MODULE(
                '__init__',
                scope=[
                    *imports,
                    pg.IMPORT.FROM("typing", "Iterator"),
                    pg.IMPORT.FROM("item_engine", "*"),
                    pg.VAR("__all__").ASSIGN(pg.LIST([pg.STR("gen_networks")])),
                    pg.DEF(
                        name="gen_networks",
                        args=pg.ARGS(
                            *[pg.VAR(f"{parser.name}_cfg").ARG(t="dict") for parser in self.parsers]),
                        t="Iterator[Network]",
                        block=[
                            pg.YIELD(
                                pg.VAR("ReflexiveNetwork" if parser.reflexive else "Network").CALL(
                                    pg.VAR("function").ARG(pg.VAR(parser.name)),
                                    pg.VAR("input_cls").ARG(pg.VAR(parser.input_cls.__name__)),
                                    pg.VAR("output_cls").ARG(pg.VAR(parser.output_cls.__name__)),
                                    pg.VAR("to_ignore").ARG(pg.LIST(list(map(repr, parser.skips)))),
                                    pg.VAR(f"{parser.name}_cfg").AS_KWARG
                                )
                            )
                            for parser in self.parsers
                        ]
                    )
                ]),
            *([] if self.operators is None else [self.operators]),
            *[parser.code for parser in self.parsers]
        )

    def build(self, root: str = os.curdir, allow_overwrite: bool = False) -> None:
        self.data().code().save(root=root, allow_overwrite=allow_overwrite)

    def data(self) -> EngineData:
        return EngineData(
            self.name,
            *[parser.data() for parser in self.parsers],
            materials=self.operators
        )


########################################################################################################################
# DATA TO CODE
########################################################################################################################


class ActionSelectData:
    def __init__(self, cases: Dict[ACTION, STATE]):
        self.cases: Dict[ACTION, STATE] = cases

    def code(self, item: pg.VAR, formal: bool) -> pg.BLOCK:
        rtype = pg.RETURN if formal else pg.YIELD

        return pg.BLOCK(*[
            rtype(pg.ARGS(pg.STR(action), pg.INT(value) if isinstance(value, int) else pg.STR(value)))
            for action, value in self.cases.items()
        ])


class GroupSelectData:
    def __init__(self, cases: Dict[Group, ActionSelectData], default: ActionSelectData):
        self.cases: Dict[Group, ActionSelectData] = cases
        self.default: ActionSelectData = default

    def code(self, item: pg.VAR, formal: bool) -> pg.SWITCH:
        return pg.SWITCH(
            cases=[(group.condition(item), asd.code(item, formal)) for group, asd in self.cases.items()],
            default=self.default.code(item, formal)
        )


class OriginSelectData:
    def __init__(self, cases: Dict[NT_STATE, GroupSelectData]):
        self.cases: Dict[NT_STATE, GroupSelectData] = cases

    def code(self, current: pg.VAR, item: pg.VAR, formal: bool) -> pg.SWITCH:
        return pg.SWITCH(
            cases=[(current.GETATTR("value").EQ(pg.INT(value)), gsd.code(item, formal)) for value, gsd in
                   self.cases.items()],
            default=pg.EXCEPTION(pg.FSTR("value = {current.value!r}")).RAISE()
        )


class ParserData:
    def __init__(self,
                 name: str,
                 input_cls: Type[Element],
                 output_cls: Type[Element],
                 osd: OriginSelectData,
                 formal: bool,

                 skips: List[str] = None,
                 reflexive: bool = False
                 ):
        self.name: str = name
        self.osd: OriginSelectData = osd
        self.input_cls: Type[Element] = input_cls
        self.output_cls: Type[Element] = output_cls
        self.formal: bool = formal

        self.skips: List[str] = skips or []
        self.reflexive: bool = reflexive

    def code(self) -> pg.MODULE:
        current = pg.VAR("current")
        item = pg.VAR("item")

        rtype = "Tuple[ACTION, STATE]" if self.formal else "Iterator[Tuple[ACTION, STATE]]"

        return pg.MODULE(
            self.name,
            [
                pg.IMPORT.FROM("typing", "Tuple"),
                *([] if self.formal else [pg.IMPORT.FROM("typing", "Iterator")]),
                pg.IMPORT.FROM("item_engine", ["ACTION", "STATE"]),
                pg.IMPORT.FROM(self.input_cls.__module__, self.input_cls.__name__),
                pg.IMPORT.FROM(self.output_cls.__module__, self.output_cls.__name__),
                pg.VAR("__all__").ASSIGN(pg.LIST([pg.STR(self.name)])),
                pg.DEF(
                    name=self.name,
                    args=pg.ARGS(
                        current.ARG(t=self.output_cls.__name__),
                        item.ARG(t=self.input_cls.__name__)
                    ),
                    block=self.osd.code(current, item, self.formal),
                    t=rtype
                ),
            ])

    @property
    def graph(self, **config):
        dag = BuilderGraph(**config, name=self.name)

        branch_set_nodes: Dict[STATE, Node] = {}
        errors: Dict[T_STATE, Node] = {}
        valids: Dict[T_STATE, Node] = {}

        def getnode(value: STATE):
            if isinstance(value, T_STATE):
                if value.startswith('!'):
                    if value not in errors:
                        errors[value] = dag.terminal_error_state(value)
                    return errors[value]
                else:
                    if value not in valids:
                        valids[value] = dag.terminal_valid_state(value)
                    return valids[value]
            else:
                if value not in branch_set_nodes:
                    branch_set_nodes[value] = dag.non_terminal_state(value)
                return branch_set_nodes[value]

        memory = {}

        def make_chain(origin: NT_STATE, group: Group, action: ACTION, target: STATE):
            origin_node = getnode(origin)
            target_node = getnode(target)
            k1 = (group, action, target_node)
            if k1 in memory:
                group_action_node = memory[k1]
            else:
                memory[k1] = group_action_node = dag.group_action(group, action)
                dag.link(group_action_node, target_node)

            k3 = (origin_node, group_action_node)
            if k3 not in memory:
                memory[k3] = dag.link(origin_node, group_action_node)

        for origin, gsd in self.osd.cases.items():
            for group, asd in gsd.cases.items():
                for action, target in asd.cases.items():
                    make_chain(origin, group, action, target)

            for action, target in gsd.default.cases.items():
                make_chain(origin, Group.never(), action, target)

        return dag


class EngineData:
    def __init__(self, name: str, *pds: ParserData, materials: pg.MODULE = None):
        self.name: str = name
        self.pds: Tuple[ParserData] = pds
        self.materials: Optional[pg.MODULE] = materials

    def code(self) -> pg.PACKAGE:
        imports: List[pg.STATEMENT] = []
        for parser_data in self.pds:
            imports.append(pg.IMPORT.FROM(parser_data.input_cls.__module__, parser_data.input_cls.__name__))
            imports.append(pg.IMPORT.FROM(parser_data.output_cls.__module__, parser_data.output_cls.__name__))
            imports.append(pg.IMPORT.FROM("." + parser_data.name, parser_data.name))

        return pg.PACKAGE(
            self.name,
            pg.MODULE(
                '__init__',
                scope=[
                    *imports,
                    pg.IMPORT.FROM("typing", "Iterator"),
                    pg.IMPORT.FROM("item_engine", "*"),
                    pg.VAR("__all__").ASSIGN(pg.LIST([pg.STR("gen_networks")])),
                    pg.DEF(
                        name="gen_networks",
                        args=pg.ARGS(
                            *[pg.VAR(f"{parser_data.name}_cfg").ARG(t="dict") for parser_data in self.pds]),
                        t="Iterator[Network]",
                        block=[
                            pg.YIELD(
                                pg.VAR("ReflexiveNetwork" if parser.reflexive else "Network").CALL(
                                    pg.VAR("function").ARG(pg.VAR(parser.name)),
                                    pg.VAR("input_cls").ARG(pg.VAR(parser.input_cls.__name__)),
                                    pg.VAR("output_cls").ARG(pg.VAR(parser.output_cls.__name__)),
                                    pg.VAR("to_ignore").ARG(pg.LIST(list(map(repr, parser.skips)))),
                                    pg.VAR(f"{parser.name}_cfg").AS_KWARG
                                )
                            )
                            for parser in self.pds
                        ]
                    )
                ]),
            *([] if self.materials is None else [self.materials]),
            *[parser.code() for parser in self.pds]
        )
