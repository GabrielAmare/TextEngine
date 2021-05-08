from __future__ import annotations
from typing import *

from ..constants import ACTION, STATE, NT_STATE, INDEX
from ..elements import Element
from .ElementList import ElementList
from .ElementDict import ElementDict

__all__ = ["BaseNetwork"]

E = TypeVar("E", bound=Element)
F = TypeVar("F", bound=Element)

# class E(Element):
#     def develop(self, action: ACTION, value: STATE, item) -> E:
#         pass
#
#     @classmethod
#     def EOF(cls, start: INDEX):
#         pass
#
#
# class F(Element):
#     def develop(self, action: ACTION, value: STATE, item) -> F:
#         pass
#
#     @classmethod
#     def EOF(cls, start: INDEX):
#         pass


FUNCTION = Callable[[NT_STATE, E], Iterator[Tuple[ACTION, STATE]]]


class BaseNetwork(Generic[E, F]):
    """This class builds element F from an array of elements E"""

    @staticmethod
    def _keep_terminals(tos: ElementDict[F]) -> ElementDict[F]:
        end = max(tos.keys())
        start = min(tos[end].keys())
        elements = tos[end][start]
        keep = ElementDict()
        keep.include({end: {start: elements}})
        return keep

    @staticmethod
    def _fork_elements(elements: List[F]) -> Tuple[ElementDict[F], ElementDict[F], List[F]]:
        ntos: ElementDict[F] = ElementDict()
        vts: ElementDict[F] = ElementDict()
        ets: List[F] = []
        for element in elements:
            if element.non_terminal:
                ntos.append(element)
            elif element.is_valid:
                vts.append(element)
            else:
                ets.append(element)
        return ntos, vts, ets

    def __init__(self, output_cls: Type[F], function: FUNCTION, formal: bool = False):
        self.output_cls: Type[F] = output_cls
        self.function: FUNCTION = function

        self.tis: ElementDict[E] = ElementDict()  # terminal inputs

        self.ntos: ElementDict[F] = ElementDict()  # non terminal outputs
        self.tos: ElementDict[F] = ElementDict()  # terminal outputs

        self.formal: bool = formal

    def _can_start_at(self, index: INDEX) -> bool:
        return index in self.tos if self.tos else False if self.ntos else index == 0

    def _can_continue_from(self, index: INDEX) -> bool:
        return index in self.ntos

    def _ntos_before(self, index: INDEX) -> Iterable[F]:
        yield from self.ntos.get_by_end(index)

    def _new_nto(self, index: INDEX) -> F:
        return self.output_cls(start=index, end=index, value=0)

    def _generate_from_nto(self, ti: E, nto: F) -> List[F]:
        return [nto.develop(action, value, ti) for action, value in self.function(nto.value, ti)]

    def _generate_from_layer(self, ti: E, layer: List[F]) -> List[F]:
        return [output for nto in layer for output in self._generate_from_nto(ti, nto)]

    def _build_layer(self, ti: E) -> List[F]:
        layer: List[F] = []

        if self._can_continue_from(ti.start):
            layer.extend(self._ntos_before(ti.start))

        if self._can_start_at(ti.start):
            layer.append(self._new_nto(ti.start))

        return layer

    def _add_terminals(self, tos: ElementDict[F]) -> ElementDict[F]:
        if not tos:
            return ElementDict()

        if not self.formal:
            self.tos.include(tos)
            return tos

        keep = self._keep_terminals(tos)

        if len(keep) > 1:
            raise Exception(f"[FORMAL_ERROR] Unable to pick from outputs when there's more than 1 solution")

        self.tos.include(keep)
        return keep

    def extend(self, tis: ElementList[E]) -> List[F]:
        """Return the layer generated by a list of elements"""
        layer: List[F] = []
        for ti in tis:
            layer += self.append(ti)

        return layer

    def append(self, ti: E) -> ElementDict[F]:
        """Generated and return all the terminal valid output elements that can be deduced from ``ti``"""
        assert ti.terminal
        layer: List[F] = self._build_layer(ti)

        if not layer:
            return ElementDict()  # nothing can be generated

        outputs: List[F] = self._generate_from_layer(ti, layer)

        assert all(output.end in (ti.start, ti.end) for output in outputs)
        assert all(output.start <= ti.start for output in outputs)

        ntos, vts, ets = self._fork_elements(outputs)

        if ets and not ntos and not vts:
            raise Exception(f"Parsing Error :\n{ets!r}\non : {ti!r}")

        if not ntos and not vts and not ets:
            raise Exception(f"Parsing Error :\nthe last element have generated nothing, there may be an error")

        if ntos:
            self.ntos.include(ntos)

        return self._add_terminals(vts)