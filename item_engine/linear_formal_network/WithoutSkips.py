from __future__ import annotations
from typing import Generic

from .Instance import Instance
from .constants import E, F

__all__ = ["WithoutSkips"]


class WithoutSkips(Instance, Generic[E, F]):
    def do_return(self, output: F) -> bool:
        return True

    def on_return(self, output: F) -> F:
        return output
