from dataclasses import dataclass
from typing import List, Callable, Optional, Dict

from graph37 import Node
from tools37 import CsvFile

from .base import Group, BranchSet
from .constants import ACTION, STATE, NT_STATE, T_STATE
from .BuilderGraph import BuilderGraph

import python_generator as pg

GBS = Callable[[BranchSet], int]

__all__ = [
    "L0", "L1", "L2", "L3", "L4", "L5", "L6",
    "F0", "F1"
]


@dataclass
class L0:
    action: ACTION
    value: STATE

    @property
    def code(self) -> pg.YIELD:
        return pg.YIELD(line=f"{self.action!r}, {self.value!r}")


@dataclass
class L1:
    cases: List[L0]

    @property
    def code(self) -> pg.LINES:
        return pg.LINES(lines=[case.code for case in self.cases])


@dataclass
class F0:
    """formal L0"""
    action: ACTION
    value: STATE

    @property
    def code(self) -> pg.RETURN:
        return pg.RETURN(line=f"{self.action!r}, {self.value!r}")


@dataclass
class F1:
    """formal L1"""
    case: F0

    @property
    def code(self) -> pg.LINES:
        return pg.LINES(lines=[self.case.code])


@dataclass
class L2:
    group: Group
    l1: L1

    @property
    def code(self) -> pg.IF:
        return pg.IF(cond=self.group.condition, body=self.l1.code)


@dataclass
class L3:
    cases: List[L2]
    default: Optional[L1]

    @property
    def code(self) -> pg.SWITCH:
        return pg.SWITCH(
            ifs=[case.code for case in self.cases],
            default=self.default.code if self.default else None
        )


@dataclass
class L4:
    value: NT_STATE
    switch: L3
    always: Optional[L1] = None

    @property
    def code(self) -> pg.IF:
        switch: pg.SWITCH = self.switch.code

        return pg.IF(
            cond=pg.EQ("value", repr(self.value)),
            body=pg.LINES([switch, self.always.code]) if self.always else switch
        )


@dataclass
class L5:
    cases: List[L4]

    @property
    def code(self) -> pg.SWITCH:
        return pg.SWITCH(
            ifs=[l4.code for l4 in self.cases],
            default=pg.RAISE(pg.EXCEPTION("f'\\nvalue: {value!r}\\nitem: {item!r}'"))
        )


@dataclass
class L6:
    name: str
    l5: L5

    @property
    def code(self) -> pg.MODULE:
        return pg.MODULE(items=[
            pg.FROM_IMPORT("typing", pg.ARGS("Iterator", "Tuple", "Union")),
            pg.SETATTR(k="__all__", v=pg.LIST([pg.STR(self.name)])),
            pg.DEF(
                name=self.name,
                args=pg.ARGS("value: int", "item"),
                body=self.l5.code,
                type="Iterator[Tuple[str, Union[int, str]]]"
            ),
        ])

    def to_csv(self, fp: str) -> None:
        data = []
        for l4 in self.l5.cases:
            for l2 in l4.switch.cases:
                if l2.l1.cases:
                    for l0 in l2.l1.cases:
                        data.append(dict(
                            origin=str(l4.value),
                            group=str(l2.group).replace('\n', ''),
                            action=l0.action,
                            target=l0.value
                        ))

            group = Group.never()
            if l4.switch.default.cases:
                for l0 in l4.switch.default.cases:
                    data.append(dict(
                        origin=str(l4.value),
                        group=str(group).replace('\n', ''),
                        action=l0.action,
                        target=l0.value
                    ))

            # group = Group.always()
            # if l4.always.cases:
            #     for l0 in l4.always.cases:
            #         data.append(dict(
            #             origin=str(l4.value),
            #             group=str(group).replace('\n', ''),
            #             action=l0.action,
            #             target=l0.value
            #         ))

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

            #
            # k1 = (action, target_node)
            # if k1 in memory:
            #     action_node = memory[k1]
            # else:
            #     memory[k1] = action_node = dag.action(action)
            #     dag.link(action_node, target_node)
            #
            # k2 = (group, action_node)
            # if k2 in memory:
            #     group_node = memory[k2]
            # else:
            #     memory[k2] = group_node = dag.group(group)
            #     dag.link(group_node, action_node)

            k3 = (origin_node, group_action_node)
            if k3 not in memory:
                memory[k3] = dag.link(origin_node, group_action_node)

        for l4 in self.l5.cases:
            for l2 in l4.switch.cases:
                if l2.l1.cases:
                    for l0 in sorted(l2.l1.cases, key=lambda l0: not isinstance(l0.value, str)):
                        make_chain(l4.value, l2.group, l0.action, l0.value)

            group = Group(frozenset())
            if l4.switch.default.cases:
                for l0 in sorted(l4.switch.default.cases, key=lambda l0: not isinstance(l0.value, str)):
                    make_chain(l4.value, group, l0.action, l0.value)

            # group = Group(frozenset(), inverted=True)
            # if l4.always.cases:
            #     for l0 in l4.always.cases:
            #         make_chain(l4.value, group, l0.action, l0.value)

        return dag
