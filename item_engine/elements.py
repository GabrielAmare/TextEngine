from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .constants import ACTION, T_STATE, NT_STATE, STATE, INDEX

__all__ = ["Element", "OPTIONS"]


@dataclass(frozen=True, order=True)
class Element:
    start: INDEX
    end: INDEX
    value: STATE

    @property
    def span(self) -> Tuple[INDEX, INDEX]:
        return self.start, self.end

    @property
    def terminal(self) -> bool:
        return isinstance(self.value, T_STATE)

    @property
    def non_terminal(self):
        return isinstance(self.value, NT_STATE)

    @property
    def is_error(self):
        return self.terminal and self.value.startswith('!')

    @property
    def is_valid(self):
        return self.terminal and not self.value.startswith('!')

    def develop(self, action: ACTION, value: STATE, item: Element) -> Element:
        raise NotImplementedError

    @classmethod
    def EOF(cls, start: INDEX) -> Element:
        raise NotImplementedError

    def lt(self, other: Element) -> bool:
        return self.end < other.start

    def le(self, other: Element) -> bool:
        return self.end <= other.start

    def gt(self, other: Element) -> bool:
        return self.end > other.start

    def ge(self, other: Element) -> bool:
        return self.end >= other.start

    def eq(self, other: Element) -> bool:
        return self.start == other.start and self.end == other.end

    def ne(self, other: Element) -> bool:
        return self.start != other.start or self.end != other.end

    def ol(self, other: Element) -> bool:
        if other.start < self.end:
            return other.end > self.start
        elif other.start > self.end:
            return other.end < self.start
        else:
            return False


class OPTIONS:
    @staticmethod
    def ordered(elements: List[Element]) -> bool:
        """Return True when elements are in order, it implies that there's no overlapping"""
        return all(a.le(b) for a, b in zip(elements, elements[1:]))

    @staticmethod
    def consecutive(elements: List[Element]) -> bool:
        """Return True when elements are in order and conscutive, it implies that there's no overlapping"""
        return all(a.end == b.start for a, b in zip(elements, elements[1:]))

    @staticmethod
    def ordered_layers(layers: List[List[Element]]) -> bool:
        """Return True when elements from consecutive layers are in order (for all possible pairs)"""
        return all(all(a.le(b) for a in A for b in B) for A, B in zip(layers, layers[1:]))

    @staticmethod
    def simultaneous_end(elements: List[Element]) -> bool:
        return all(a.end == b.end for a in elements for b in elements)

    @staticmethod
    def simultaneous_start(elements: List[Element]) -> bool:
        return all(a.start == b.start for a in elements for b in elements)

    @staticmethod
    def non_overlaping(elements: List[Element]):
        return all(not a.ol(b) for a in elements for b in elements if a is not b)
