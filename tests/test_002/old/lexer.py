from typing import Iterator, Tuple
from item_engine import NT_STATE, Element, ACTION, STATE

__all__ = ['lexer']


def lexer(value: NT_STATE, item: Element) -> Iterator[Tuple[ACTION, STATE]]:
    if value == 0:
        if item.value in '0123456789':
            yield '∈', 1
        else:
            yield '∉', '!INT'
    elif value == 1:
        if item.value in '0123456789':
            yield '∈', 1
        else:
            yield '∉', 'INT'
    else:
        raise Exception(f'\nvalue: {value!r}\nitem: {item!r}')
