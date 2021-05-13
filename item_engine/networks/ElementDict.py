from __future__ import annotations
from typing import Generic, TypeVar, List, Dict, Iterable
from ..base import Element
from ..constants import INDEX

__all__ = ["ElementDict"]

E = TypeVar("E", bound=Element)


class ElementDict(Dict[INDEX, Dict[INDEX, List[E]]], Generic[E]):
    def __init__(self, **data):
        super().__init__(**data)

    def append(self, element: E) -> None:
        self.setdefault(element.end, {})
        self[element.end].setdefault(element.start, [])
        self[element.end][element.start].append(element)

    def extend(self, elements: Iterable[E]) -> None:
        for element in elements:
            self.append(element)

    def include(self, element_dict: Dict[INDEX, Dict[INDEX, List[E]]]) -> None:
        for end, data in element_dict.items():
            self.setdefault(end, {})
            for start, elements in data.items():
                self[end].setdefault(start, [])
                self[end][start].extend(elements)

    def get_by_end(self, end: INDEX) -> Iterable[E]:
        for _, elements in self.get(end, {}).items():
            yield from elements
