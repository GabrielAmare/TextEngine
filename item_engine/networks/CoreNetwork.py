from __future__ import annotations
from typing import *

from ..constants import ACTION, STATE, NT_STATE, INDEX
from ..elements import Element
from .BaseNetwork import BaseNetwork
from .ElementDict import ElementDict

__all__ = ["CoreNetwork"]

E = TypeVar("E", bound=Element)
F = TypeVar("F", bound=Element)

FUNCTION = Callable[[NT_STATE, E], Iterator[Tuple[ACTION, STATE]]]


class CoreNetwork(Generic[E, F]):
    def __init__(self, output_cls: Type[F], function: FUNCTION, formal: bool = False):
        self.output_cls: Type[F] = output_cls
        self.function: FUNCTION = function
        self.formal: bool = formal

        self.tis: List[E] = []  # terminal inputs

        self.ntos: ElementDict[F] = ElementDict()  # non terminal outputs
        self.tos: ElementDict[F] = ElementDict()  # terminal outputs

        self.tos_ends: Set[INDEX] = set()

    def extend(self, input_layer: List[E]):
        pass

    def append(self, terminal_input: E) -> List[F]:
        pass
