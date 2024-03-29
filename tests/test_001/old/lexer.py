from typing import Iterator, Tuple
from item_engine import NT_STATE, Element, ACTION, STATE

__all__ = ['lexer']


def lexer(value: NT_STATE, item: Element) -> Iterator[Tuple[ACTION, STATE]]:
    if value == 0:
        if item.value in '\t ':
            yield '∈', 1
        elif item.value == '\n':
            yield '∈', 'NEWLINE'
        elif item.value == '!':
            yield '∈', 'EXC'
        elif item.value == '&':
            yield '∈', 'AMPS'
        elif item.value == '(':
            yield '∈', 'LP'
        elif item.value == ')':
            yield '∈', 'RP'
        elif item.value == '*':
            yield '∈', 2
        elif item.value == '+':
            yield '∈', 'PLUS'
        elif item.value == ',':
            yield '∈', 'COMMA'
        elif item.value == '-':
            yield '∈', 'DASH'
        elif item.value == '.':
            yield '∈', 3
        elif item.value == '/':
            yield '∈', 'SLASH'
        elif item.value in '0123456789':
            yield '∈', 4
        elif item.value == '<':
            yield '∈', 5
        elif item.value == '=':
            yield '∈', 6
        elif item.value == '>':
            yield '∈', 7
        elif item.value in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_bcdefghijklmpqrstuvwxyz':
            yield '∈', 8
        elif item.value == '[':
            yield '∈', 'LB'
        elif item.value == ']':
            yield '∈', 'RB'
        elif item.value == 'a':
            yield '∈', 9
        elif item.value == 'n':
            yield '∈', 10
        elif item.value == 'o':
            yield '∈', 11
        elif item.value == '{':
            yield '∈', 'LS'
        elif item.value == '|':
            yield '∈', 'VBAR'
        elif item.value == '}':
            yield '∈', 'RS'
        else:
            yield '∉', '!KW_AND|KW_NOT|KW_OR'
    elif value == 1:
        if item.value in '\t ':
            yield '∈', 1
        else:
            yield '∉', 'WHITESPACE'
    elif value == 2:
        if item.value == '*':
            yield '∈', 'STAR_STAR'
        else:
            yield '∉', '!STAR_STAR'
    elif value == 3:
        if item.value in '0123456789':
            yield '∈', 12
        else:
            yield '∉', '!FLOAT'
    elif value == 4:
        if item.value == '.':
            yield '∈', 13
        elif item.value in '0123456789':
            yield '∈', 4
        else:
            yield '∉', 'INT'
    elif value == 5:
        if item.value == '=':
            yield '∈', 'LV_EQUAL'
        else:
            yield '∉', '!LV_EQUAL'
    elif value == 6:
        if item.value == '=':
            yield '∈', 'EQUAL_EQUAL'
        else:
            yield '∉', '!EQUAL_EQUAL'
    elif value == 7:
        if item.value == '=':
            yield '∈', 'RV_EQUAL'
        else:
            yield '∉', '!RV_EQUAL'
    elif value == 8:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            yield '∈', 8
        else:
            yield '∉', 'ID'
    elif value == 9:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmopqrstuvwxyz':
            yield '∈', 8
        elif item.value == 'n':
            yield '∈', 14
        else:
            yield '∉', 'ID'
    elif value == 10:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnpqrstuvwxyz':
            yield '∈', 8
        elif item.value == 'o':
            yield '∈', 15
        else:
            yield '∉', 'ID'
    elif value == 11:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqstuvwxyz':
            yield '∈', 8
        elif item.value == 'r':
            yield '∈', 8
        else:
            yield '∉', 'ID'
    elif value == 12:
        if item.value in '0123456789':
            yield '∈', 12
        else:
            yield '∉', 'FLOAT'
    elif value == 13:
        if item.value == '.':
            yield '∈', 12
        else:
            yield '∉', '!FLOAT'
    elif value == 14:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcefghijklmnopqrstuvwxyz':
            yield '∈', 8
        elif item.value == 'd':
            yield '∈', 8
        else:
            yield '∉', 'ID'
    elif value == 15:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrsuvwxyz':
            yield '∈', 8
        elif item.value == 't':
            yield '∈', 8
        else:
            yield '∉', 'ID'
    else:
        raise Exception(f'\nvalue: {value!r}\nitem: {item!r}')
