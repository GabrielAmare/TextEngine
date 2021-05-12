from __future__ import annotations
from typing import Generic, Dict
from dataclasses import replace

from ..constants import INDEX, POSITION

from .Instance import Instance
from .constants import E, F

__all__ = ["WithSkips"]


class WithSkips(Instance[E, F], Generic[E, F]):
    def __init__(self, model):
        super().__init__(model)
        self.positions: Dict[INDEX, POSITION] = {}
        self.max_position: POSITION = 0

    def get_position(self, index: INDEX) -> POSITION:
        if index in self.positions:
            return self.positions[index]
        else:
            self.positions[index] = position = self.max_position
            self.max_position += 1
            return position

    def make_bridge(self, output: F):
        if output.end not in self.positions:
            self.positions[output.end] = self.get_position(output.start)

    def do_return(self, output: F) -> bool:
        if output.value in self.model.skips:
            self.make_bridge(output)
            return False
        else:
            return True

    def on_return(self, output: F) -> F:
        return replace(output, start=self.get_position(output.start), end=self.get_position(output.end))
