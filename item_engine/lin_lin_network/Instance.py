from __future__ import annotations
from typing import Generic, List, Optional, Iterator, Generator

from ..constants import INDEX

from .constants import E, F

__all__ = ["Instance"]


class Instance(Generic[E, F]):
    def __init__(self, model):
        self.model = model
        self.outputs: List[F] = []

        self.log: List[List[str]] = []  # for debug purpose

        self.current: Optional[F] = None
        self.current_end: INDEX = 0

    def __iter__(self) -> Iterator[F]:
        return iter(self.outputs)

    def i_generate(self, inputs: Iterator[E]) -> Generator[F, None, None]:
        yield from self(inputs)

    def generate(self, inputs: Iterator[E]) -> List[F]:
        self.outputs.extend(self.i_generate(inputs))
        return self.outputs

    def new_at(self, index: INDEX) -> None:
        self.current = self.model.output_cls(start=index, end=index, value=0)
        self.current_end = index

    def set_at(self, current: Optional[F]) -> None:
        self.current = current
        self.current_end = -1 if current is None else current.end

    def handle(self, input_: E) -> Generator[F, None, None]:
        action, value = self.model.function(self.current, input_)
        output: F = self.current.develop(action, value, input_)

        assert output.end in {self.current.end, input_.end}  # for debug purpose
        self.log[-1].append(f"{self.current!r} + {input_!r} -> {output!r}")  # for debug purpose

        if output.is_valid:
            self.new_at(output.end)
            if self.do_return(output):
                yield self.on_return(output)
        elif output.is_error:
            self.set_at(None)
        else:
            self.set_at(output)

    def __call__(self, inputs: Iterator[E]) -> Generator[F, None, None]:
        self.new_at(0)
        for input_ in inputs:
            if self.current is None:
                raise SyntaxError(input_)

            assert input_.terminal, "Network inputs must be terminal elements"  # for debug purpose
            assert self.current_end == input_.start, "Network inputs must be consecutive to each other"  # for debug purpose

            self.log.append([])  # for debug purpose
            while self.current_end == input_.start:
                yield from self.handle(input_)

        if self.current is not None:
            eof = self.model.input_cls.EOF(self.current.to)
            yield from self.handle(eof)

    def do_return(self, output: F) -> bool:
        raise NotImplementedError

    def on_return(self, output: F) -> F:
        raise NotImplementedError
