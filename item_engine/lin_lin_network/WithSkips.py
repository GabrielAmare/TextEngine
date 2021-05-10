from __future__ import annotations
from typing import Generic
from dataclasses import replace

from ..constants import POSITION

from .Instance import Instance
from .constants import E, F

__all__ = ["WithSkips"]


class WithSkips(Instance, Generic[E, F]):
    def __init__(self, model):
        super().__init__(model)
        self.position: POSITION = 0

    def do_return(self, output: F) -> bool:
        return output.value not in self.model.skips

    def on_return(self, output: F) -> F:
        self.position += 1
        return replace(output, start=self.position - 1, end=self.position)
