from dataclasses import dataclass
from typing import List, Union, Callable, Optional

from .items import *
from .branches import *

import python_generator as pg

GBS = Callable[[BranchSet], int]

__all__ = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")


@dataclass
class L0:
    action: str
    value: Union[int, str]

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
    value: int
    switch: L3
    always: Optional[L1]

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
    def code(self) -> pg.DEF:
        return pg.DEF(
            name=self.name,
            args=pg.ARGS("value: int", "item"),
            body=self.l5.code,
            type_="Iterator[Tuple[str, Union[int, str]]]"
        )
