from typing import TypeVar
from ..elements import Element

__all__ = ["E", "F"]

E = TypeVar("E", bound=Element)
F = TypeVar("F", bound=Element)

