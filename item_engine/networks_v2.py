from __future__ import annotations
from dataclasses import replace
from typing import *

from item_engine.constants import NT_STATE, ACTION, STATE, INCLUDE, EXCLUDE
from item_engine.elements import Element

E = TypeVar("E", bound=Element)
F = TypeVar("F", bound=Element)

FORMAL_FUNCTION = Callable[[NT_STATE, E], Tuple[ACTION, STATE]]


class FormalLinearNetworkModel(Generic[E, F]):
    """works when two EXCLUDE actions cannot be consecutive"""

    def __init__(self, input_cls: Type[E], output_cls: Type[F], function: FORMAL_FUNCTION, skips: List[str] = None):
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
        self.function: FORMAL_FUNCTION = function
        self.skips: List[str] = skips

    @property
    def instance(self) -> Instance[E, F]:
        """Generate a new instance of the network"""
        if self.skips:
            return self.InstanceWithSkips(model=self)
        else:
            return self.InstanceWithoutSkips(model=self)

    def tokenize(self, inputs: Iterator[E]) -> List[F]:
        return self.instance.tokenize(inputs)

    def itokenize(self, inputs: Iterator[E]) -> Generator[F, None, None]:
        yield from self.instance.itokenize(inputs)

    def parse(self, inputs: Iterator[E]) -> Instance[E, F]:
        instance = self.instance
        instance.tokenize(inputs)
        return instance

    class Instance(Generic[E, F]):
        def __init__(self, model: FormalLinearNetworkModel[E, F]):
            self.model: FormalLinearNetworkModel[E, F] = model
            self.outputs: List[F] = []

            self.log: List[List[str]] = []  # for debug purpose

        def __call__(self, inputs: Iterator[E]) -> Generator[F, None, None]:
            raise NotImplementedError

        def __iter__(self) -> Iterator[F]:
            return iter(self.outputs)

        def itokenize(self, inputs: Iterator[E]) -> Generator[F, None, None]:
            yield from self(inputs)

        def tokenize(self, inputs: Iterator[E]) -> List[F]:
            self.outputs.extend(self.itokenize(inputs))
            return self.outputs


if __name__ == '__main__':
    from item_engine.textbase import make_characters, Char, Token

    calls_to = {}


    def memorize(function):
        cache = {}

        def wrapper(value, element):
            key = (value, element.value)
            global calls_to
            calls_to.setdefault(key, 0)
            calls_to[key] += 1
            if key in cache:
                return cache[key]
            else:
                cache[key] = result = function(value, element)
                return result

        return wrapper


    @memorize
    def function(value: NT_STATE, element) -> Tuple[ACTION, STATE]:
        """
        parser for :
            VAR = 'abcdefghijklmnopqrstuvwxyz'+
            NUM = '0123456789'+
            VAR_NUM = 'abcdefghijklmnopqrstuvwxyz'+ '0123456789'+
            EQUAL = '='
            PLUS = '+'
            PLUS_EQUAL = '+='
            PLUS_PLUS = '++'
            LP = '('
            RP = ')'
        """
        if value == 0:
            if element.value == '=':
                return INCLUDE, 'EQUAL'
            elif element.value == '+':
                return INCLUDE, 7
            elif element.value == '(':
                return INCLUDE, 'LP'
            elif element.value == ')':
                return INCLUDE, 'RP'
            elif element.value == '/':
                return INCLUDE, 'SLASH'
            elif element.value == '-':
                return INCLUDE, 'DASH'
            elif element.value == ' ':
                return INCLUDE, 6
            elif element.value in 'abcefghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif element.value in 'd':
                return INCLUDE, 3
            elif element.value in '0123456789':
                return INCLUDE, 8
            else:
                return EXCLUDE, '!'
        elif value == 1:
            if element.value in 'abcdefghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif element.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'VAR'
        elif value == 2:
            if element.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'VAR_NUM'
        elif value == 3:
            if element.value == 'e':
                return INCLUDE, 4
            elif element.value in 'abcdfghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif element.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'VAR'
        elif value == 4:
            if element.value == 'f':
                return INCLUDE, 5
            elif element.value in 'abcdeghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif element.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'VAR'
        elif value == 5:
            if element.value in 'abcdefghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif element.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'KW_DEF'
        elif value == 6:
            if element.value == ' ':
                return INCLUDE, 6
            else:
                return EXCLUDE, 'SPACE'
        elif value == 7:
            if element.value == '+':
                return INCLUDE, 'PLUS_PLUS'
            elif element.value == '=':
                return INCLUDE, 'PLUS_EQUAL'
            else:
                return EXCLUDE, 'PLUS'
        elif value == 8:
            if element.value in '0123456789':
                return INCLUDE, 8
            else:
                return EXCLUDE, 'NUM'
        else:
            raise Exception(f"invalid value : {value!r}")


    net = FormalLinearNetworkModel(
        input_cls=Char,
        output_cls=Token,
        function=function,
        skips=["SPACE"]
    )

    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789+/=() "

    import time
    import random

    size = 10_000
    text = ''.join(random.choice(alphabet) for _ in range(size))
    # print(repr(text))
    t = time.time()
    try:
        tokens = net.tokenize(make_characters(text))
        d = time.time() - t
        print(f"{round((1e6 * d) / len(text))} μs/char [{len(text)} chars]")
        print(f"{round((1e6 * d) / len(tokens))} μs/token [{len(tokens)} tokens]")
        print(f"total time : {round(d, 3)} seconds")
        print()
    except SyntaxError as e:
        print(repr(text))
        print('|' + ''.join('^' if e.args[0].start == index else ' ' for index in range(len(text))) + '|')
        raise e

    len_keys = len(calls_to.keys())
    max_call = max(calls_to.values())
    sum_call = sum(calls_to.values())

    print(f"memorize\n"
          f"number of cases : {len_keys}\n"
          f"maximum calls to a single case : {max_call}\n"
          f"mean calls to a single case : {sum_call / max_call}")

    for key, val in calls_to.items():
        if val >= 0.75 * max_call:
            print(f"{key} occured {val} times")
