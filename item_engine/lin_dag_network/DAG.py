from typing import Dict, Tuple, List, Generic, Generator, Iterator, TypeVar

from ..constants import INDEX
from ..elements import Element

__all__ = ["DAG"]

E = TypeVar("E", bound=Element)


class DAG(Dict[Tuple[INDEX, INDEX], List[E]], Generic[E]):
    def get_by_end(self, end: INDEX) -> Generator[E, None, None]:
        for span, elements in self.items():
            if span[1] == end:
                yield from elements

    def get_by_start(self, start: INDEX) -> Generator[E, None, None]:
        for span, elements in self.items():
            if span[0] == start:
                yield from elements

    def append(self, element: E):
        span = element.span
        self.setdefault(span, [])
        self[span].append(element)

    def extend(self, elements: Iterator[E]):
        for element in elements:
            self.append(element)

    def __iter__(self) -> Generator[E, None, None]:
        for elements in self.values():
            yield from elements
