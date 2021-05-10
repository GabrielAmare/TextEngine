from typing import TypeVar, Callable, Tuple
from ..constants import NT_STATE, ACTION, STATE
from ..elements import Element

__all__ = ["E", "F", "FORMAL_FUNCTION"]

E = TypeVar("E", bound=Element)
F = TypeVar("F", bound=Element)

FORMAL_FUNCTION = Callable[[NT_STATE, E], Tuple[ACTION, STATE]]
