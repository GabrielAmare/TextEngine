from typing import Generic, List, Iterator

from .constants import E

from ..constants import INDEX

__all__ = ["Generation"]


class Generation(Generic[E]):
    def __init__(self, start: INDEX, end: INDEX):
        self.at: INDEX = start
        self.to: INDEX = end

        self.non_terminals: List[E] = []
        self.terminals_start: List[E] = []
        self.terminals_end: List[E] = []

    def __repr__(self):
        return "non-terminals:\n" + "\n".join(map(repr, self.non_terminals)) + \
               "terminals:\n" + "\n".join(map(repr, self.terminals))

    @property
    def terminals(self):
        return self.terminals_start + self.terminals_end

    def append(self, output: E):
        if output.terminal:
            if output.end == self.to:
                self.terminals_end.append(output)
            elif output.end == self.at:
                self.terminals_start.append(output)
            else:
                assert False
        elif output.end == self.to:
            self.non_terminals.append(output)
        elif output.end == self.at:
            pass
        else:
            raise Exception

    def extend(self, outputs: Iterator[E]):
        for output in outputs:
            self.append(output)
