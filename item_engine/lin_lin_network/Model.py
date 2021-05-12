from __future__ import annotations
from typing import Callable, Tuple, List, Iterator, Generator, Type, Generic

from ..constants import NT_STATE, ACTION, STATE

from .Instance import Instance
from .WithSkips import WithSkips
from .WithoutSkips import WithoutSkips

from .constants import E, F

__all__ = ["Model"]

FUNCTION = Callable[[F, E], Tuple[ACTION, STATE]]


class Model(Generic[E, F]):
    """works when two EXCLUDE actions cannot be consecutive"""

    def __init__(self, input_cls: Type[E], output_cls: Type[F], function: FUNCTION, skips: List[str] = None):
        """

        :param input_cls: The Element class of the inputs
        :param output_cls: The Element class of the outputs
        :param function: The function that generates action & new value from the old value and an input element
        :param skips: The terminal valid values that must be skipped (refactoring the positions of the outputs elements)
        """
        if skips is None:
            skips = []
        self.input_cls: Type[E] = input_cls
        self.output_cls: Type[F] = output_cls
        self.function: FUNCTION = function
        self.skips: List[str] = skips

    @property
    def instance(self) -> Instance[E, F]:
        """Generate a new instance of the network"""
        if self.skips:
            return WithSkips(model=self)
        else:
            return WithoutSkips(model=self)

    def generate(self, inputs: Iterator[E]) -> List[F]:
        return self.instance.generate(inputs)

    def i_generate(self, inputs: Iterator[E]) -> Generator[F, None, None]:
        yield from self.instance.i_generate(inputs)

    def parse(self, inputs: Iterator[E]) -> Instance[E, F]:
        instance = self.instance
        instance.generate(inputs)
        return instance
