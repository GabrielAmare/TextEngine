from dataclasses import dataclass
from typing import *
from item_engine.base import Element
from item_engine.constants import ACTION, STATE, INDEX

E = TypeVar("E", bound=Element)
F = TypeVar("F", bound=Element)

__all__ = ["Model", "Network"]


@dataclass(frozen=True, order=True)
class Model(Generic[E, F]):
    input_cls: Type[E]
    output_cls: Type[F]
    func: Callable[[F, E], Iterator[Tuple[ACTION, STATE]]]
    consecutive_inputs: bool  # this forces the inputs to be a consecutive list of elements !
    consecutive_outputs: bool  # this forces the outputs to be generated as a consecutive list of elements !
    formal: bool

    def new(self, at: INDEX) -> F:
        return self.output_cls(at=at, to=at, value=0)

    def eof(self, at: INDEX) -> E:
        return self.input_cls.EOF(at=at)

    def gen(self, current: F, input_: E) -> Iterator[F]:
        for action, value in self.func(current, input_):
            yield current.develop(action, value, input_)


class Network(Generic[E, F]):
    def __init__(self, model: Model[E, F], at: INDEX = 0):
        self.model: Model[E, F] = model
        self.at: INDEX = at
        self.to: INDEX = at
        self.currents: Dict[INDEX, List[F]] = {}
        self._new_current(at)

        self.input_to: int = at
        self.output_to: int = at

    def _gen(self, input_: E) -> Iterator[F]:
        """Generate outputs from ``currents`` and ``input_``"""
        if input_.at not in self.currents and not self.model.formal:
            self._new_current(input_.at)

        for current in self.currents.get(input_.at, []):
            for output in self.model.gen(current, input_):
                yield output

    def _add_current(self, current: F):
        """Add a new ``current`` element to the network"""
        to = current.to
        if to in self.currents:
            if current not in self.currents[to]:
                self.currents[to].append(current)
        else:
            self.currents[to] = [current]

    def _new_current(self, at: INDEX):
        """Create a new ``current`` element and add it to the network"""
        self._add_current(self.model.new(at))

    def add(self, input_: E) -> Iterator[F]:
        """Add an ``input_`` to the network and yields the ``outputs`` that can be generated from it"""
        if self.model.consecutive_inputs:
            assert self.input_to == input_.at, "inputs must be consecutive"
        self.input_to = input_.to

        # print(input_)
        for output in self._gen(input_):
            # print("   ", repr(output))
            if not output.is_terminal:
                self._add_current(output)
            elif output.is_valid:
                if self.model.consecutive_outputs:
                    assert output.at == self.output_to

                self.output_to = output.to
                self._new_current(output.to)

                yield output
            else:
                pass


from item_engine.textbase import Char, Token, make_characters

letters = "abcdefghijklmnopqrstuvwxyz"
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
digits = "0123456789"


def lexer(o: Token, i: Char) -> Iterator[Tuple[ACTION, STATE]]:
    if o.value == 0:
        if i.value == '.':
            yield '∈', 1
        elif i.value == '(':
            yield '∈', 'LP'
        elif i.value == ')':
            yield '∈', 'RP'
        elif i.value == ',':
            yield '∈', 'COMMA'
        elif i.value == "d":
            yield '∈', 6
        elif i.value in '0123456789':
            yield '∈', 2
        elif i.value in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcefghijklmnopqrstuvwxyz':
            yield '∈', 3
        else:
            yield '∉', '!FLOAT|ID|INT'
    elif o.value == 1:  # r'.'
        if i.value in '0123456789':
            yield '∈', 4
        else:
            yield '∉', '!FLOAT'
    elif o.value == 2:  # r'\d+'
        if i.value == '.':
            yield '∈', 5
        elif i.value in '0123456789':
            yield '∈', 2
        else:
            yield '∉', 'INT'
    elif o.value == 3:
        if i.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            yield '∈', 3
        else:
            yield '∉', 'ID'
    elif o.value == 4:  # r'\.\d+'
        if i.value in '0123456789':
            yield '∈', 4
        else:
            yield '∉', 'FLOAT'
    elif o.value == 5:
        if i.value in '0123456789':
            yield '∈', 5
        else:
            yield '∉', 'FLOAT'
    elif o.value == 6:
        if i.value == 'e':
            yield '∈', 7
        elif i.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdfghijklmnopqrstuvwxyz':
            yield '∈', 3
        else:
            yield '∉', 'ID'
    elif o.value == 7:
        if i.value == 'f':
            yield '∈', 8
        elif i.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdeghijklmnopqrstuvwxyz':
            yield '∈', 3
        else:
            yield '∉', 'ID'
    elif o.value == 8:
        if i.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            yield '∈', 3
        else:
            yield '∉', 'DEF'
    else:
        raise Exception(o)


from tools37 import ReprTable


@dataclass(frozen=True, order=True)
class Engine(Model):
    def i_tokenize(self, text: str) -> Iterator[Token]:
        chars = make_characters(text, eof=True)
        network = Network(model=self, at=0)
        for char in chars:
            for token in network.add(char):
                yield token

    def tokenize(self, text: str) -> List[Token]:
        return list(self.i_tokenize(text))


def main():
    engine = Engine(
        input_cls=Char,
        output_cls=Token,
        func=lexer,
        consecutive_inputs=True,
        consecutive_outputs=False,
        formal=False
    )

    texts = [
        "x",
        "xyz",
        "xy12",
        "245",
        "12.34",
        ".56",
        "102.",
        "1.2.3x",
        "def",
        "udef",
        "defs",
        "def function(x, y)"
    ]
    for text in texts:
        tokens = engine.tokenize(text)

        print(ReprTable.from_items(tokens, dict(
            span=lambda token: str(token.span),
            value=lambda token: token.value,
            content=lambda token: repr(token.content)
        )))
        print()


if __name__ == '__main__':
    main()
