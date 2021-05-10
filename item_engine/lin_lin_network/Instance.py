from __future__ import annotations
from typing import Generic, List, Optional, Iterator, Generator

from .constants import E, F

__all__ = ["Instance"]


class Instance(Generic[E, F]):
    def __init__(self, model):
        self.model = model
        self.outputs: List[F] = []

        self.log: List[List[str]] = []  # for debug purpose

        self.current: Optional[F] = None

    def __iter__(self) -> Iterator[F]:
        return iter(self.outputs)

    def i_tokenize(self, inputs: Iterator[E]) -> Generator[F, None, None]:
        yield from self(inputs)

    def tokenize(self, inputs: Iterator[E]) -> List[F]:
        self.outputs.extend(self.i_tokenize(inputs))
        return self.outputs

    def generate(self, input_: E) -> F:
        action, value = self.model.function(self.current.value, input_)
        n: F = self.current.develop(action, value, input_)
        assert n.end in {self.current.end, input_.end}  # for debug purpose
        self.log[-1].append(f"{self.current!r} + {input_!r} -> {n!r}")  # for debug purpose
        return n

    def finalize(self, output: F) -> Optional[F]:
        self.current = self.model.output_cls(start=output.end, end=output.end, value=0)
        if self.do_return(output):
            return self.on_return(output)

    def handle(self, input_: E, eof: bool = False) -> Optional[F]:
        output = self.generate(input_)

        if output.non_terminal:
            self.current = output
        elif output.is_valid:
            return self.finalize(output)
        elif not eof:
            raise SyntaxError(input_)

    def __call__(self, inputs: Iterator[E]) -> Generator[F, None, None]:
        self.current = self.model.output_cls(start=0, end=0, value=0)

        for input_ in inputs:
            assert input_.terminal, "Network inputs must be terminal elements"  # for debug purpose
            if self.current is None:
                raise SyntaxError(input_)

            self.log.append([])  # for debug purpose
            while self.current.end == input_.start:
                output = self.handle(input_)
                if output is not None:
                    yield output

        if self.current is not None:
            eof = self.model.input_cls.EOF(self.current.end)
            output = self.handle(eof, eof=True)
            if output is not None:
                yield output

    def do_return(self, output: F) -> bool:
        raise NotImplementedError

    def on_return(self, output: F) -> F:
        raise NotImplementedError
