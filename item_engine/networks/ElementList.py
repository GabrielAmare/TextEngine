from typing import TypeVar, Generic, List, Iterable
from ..elements import Element

__all__ = ["ElementList"]

E = TypeVar("E", bound=Element)


class ElementList(Generic[E]):
    """
        Correspond to a strict list of elements E,
        it can be used to represent unambiguous situations,
        useful in formal grammars as there can't be ambiguity
    """

    def __init__(self, elements: List[E]):
        assert elements, "there must be elements"
        assert elements[0].start == 0, "the first element must start at index 0"
        assert elements[-1].value == "EOF", "the last element must be an End Of File"
        assert elements[-1].start == elements[-1].end, "EOF element must have length == 0"
        assert all(element.terminal for element in elements), \
            "all elements must be terminal"
        assert all(a.end == b.start for a, b in zip(elements, elements[1:])), \
            "all consecutive pair of element must start/end at the same index"
        self.elements: List[E] = elements

    def __iter__(self) -> Iterable[E]:
        return iter(self.elements)
