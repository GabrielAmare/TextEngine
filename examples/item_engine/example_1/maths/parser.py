from item_engine import ACTION, STATE
from item_engine.textbase.elements import Lemma, Token
from typing import Iterator, Tuple


__all__ = ['parser']


def parser(current: Lemma, item: Token) -> Iterator[Tuple[ACTION, STATE]]:
    if current.value == 0:
        if item.value == 'INT':
            yield 'as:c0', 1
        elif item.value == 'VAR':
            yield 'as:c0', 2
        else:
            yield '∉', '!__MUL__|__POW__'
    elif current.value == 1:
        if item.value == 'VAR':
            yield 'as:c1', '__MUL__'
        else:
            yield '∉', '!__MUL__'
    elif current.value == 2:
        if item.value == 'INT_POW':
            yield 'as:c1', '__POW__'
        else:
            yield '∉', '!__POW__'
    else:
        raise Exception(f'value = {current.value!r}')
