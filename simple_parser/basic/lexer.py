from typing import Iterator, Tuple
from item_engine import NT_STATE, Element, ACTION, STATE

__all__ = ['lexer']


def lexer(value: NT_STATE, item: Element) -> Iterator[Tuple[ACTION, STATE]]:
    if value == 0:
        if item.value == '.':
            yield '∈', 1
        elif item.value in '0123456789':
            yield '∈', 2
        elif item.value in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            yield '∈', 3
        else:
            yield '∉', '!FLOAT|ID|INT'
    elif value == 1:
        if item.value in '0123456789':
            yield '∈', 4
        else:
            yield '∉', '!FLOAT'
    elif value == 2:
        if item.value == '.':
            yield '∈', 5
        elif item.value in '0123456789':
            yield '∈', 2
        else:
            yield '∉', 'INT'
    elif value == 3:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            yield '∈', 3
        else:
            yield '∉', 'ID'
    elif value == 4:
        if item.value in '0123456789':
            yield '∈', 4
        else:
            yield '∉', 'FLOAT'
    elif value == 5:
        if item.value == '.':
            yield '∈', 4
        else:
            yield '∉', '!FLOAT'
    else:
        raise Exception(f'\nvalue: {value!r}\nitem: {item!r}')
