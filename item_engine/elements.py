from __future__ import annotations
from .constants import ACTION, T_STATE, NT_STATE, STATE, INDEX

__all__ = ["Element"]


class Element:
    def __init__(self, start: INDEX, end: INDEX, value: STATE):
        self.start: INDEX = start
        self.end: INDEX = end
        self.value: STATE = value

    def __hash__(self) -> int:
        return hash((type(self), self.start, self.end, self.value))

    def __lt__(self, other: Element) -> bool:
        return hash(self) < hash(other)

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
