from __future__ import annotations
from typing import Generic, List, Iterator, Generator

from ..constants import INDEX

from .constants import E, F
from .DAG import DAG
from .Generation import Generation

__all__ = ["Instance"]


class Instance(Generic[E, F]):
    def __init__(self, model, debug: bool = True):
        self.model = model
        self.outputs: DAG[F] = DAG()

        self.debug: bool = debug  # for debug purpose
        self.log: List[List[str]] = []  # for debug purpose

        # current non-terminal elements stored
        # (they all end at the same index which is where the latest terminal input ended)
        self.currents: List[F] = [self.new_at(0)]
        self.current_end: INDEX = 0

    def __iter__(self) -> Generator[F, None, None]:
        for outputs in self.outputs.values():
            yield from outputs

    def i_generate(self, inputs: Iterator[E]) -> Generator[F, None, None]:
        yield from self(inputs)

    def generate(self, inputs: Iterator[E]) -> DAG[F]:
        self.outputs.extend(self.i_generate(inputs))
        return self.outputs

    def new_at(self, index: INDEX) -> F:
        return self.model.output_cls(start=index, end=index, value=0)

    def generate_output(self, current: F, input_: E) -> Generator[F, None, None]:
        for action, value in self.model.function(current, input_):
            output: F = current.develop(action, value, input_)
            assert output.end in {input_.start, input_.end}  # for debug purpose
            yield output

    def generate_layer(self, input_: E) -> List[F]:
        generation: Generation[F] = Generation(input_.start, input_.end)

        for current in self.currents:
            generation.extend(self.generate_output(current, input_))

        if generation.terminals_start:
            current = self.new_at(input_.start)
            generation.extend(self.generate_output(current, input_))

        if generation.terminals_end:
            current = self.new_at(input_.end)
            generation.append(current)

        terminals: List[F] = []

        for output in generation.terminals:
            if output.is_valid:
                if self.do_return(output):
                    output = self.on_return(output)
                    terminals.append(output)

        self.currents = generation.non_terminals
        self.current_end = generation.end

        return terminals

    def __call__(self, inputs: Iterator[E]) -> Generator[F, None, None]:
        """
            The outputed elements are naturally sorted by increasing end indexes

            # to verify : for elements with same end index, they come out sorted by increasing start
        """
        for input_ in inputs:
            if not self.currents:
                if self.model.allow_gaps:
                    self.currents.append(self.new_at(input_.start))
                else:
                    raise SyntaxError(input_)

            assert input_.terminal, "Network inputs must be terminal elements"  # for debug purpose
            assert input_.start == self.current_end
            yield from self.generate_layer(input_)

        if self.currents:
            eof = self.model.input_cls.EOF(self.current_end)
            yield from self.generate_layer(eof)

    def do_return(self, output: F) -> bool:
        raise NotImplementedError

    def on_return(self, output: F) -> F:
        raise NotImplementedError
