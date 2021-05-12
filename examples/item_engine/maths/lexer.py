from typing import Iterator, Tuple, Union

__all__ = ['lexer']


def lexer(value: int, item) -> Iterator[Tuple[str, Union[int, str]]]:
    if value == 0:
        if item.value in '\t ':
            yield '∈', 1
        elif item.value == '\n':
            yield '∈', 2
        elif item.value == '!':
            yield '∈', 'EXC'
        elif item.value == '&':
            yield '∈', 'AMPS'
        elif item.value == '(':
            yield '∈', 'LP'
        elif item.value == ')':
            yield '∈', 'RP'
        elif item.value == '*':
            yield '∈', 'STAR'
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
        elif item.value == '^':
            yield '∈', 'HAT'
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
        elif item.value in '²³¹⁰⁴⁵⁶⁷⁸⁹':
            yield '∈', 12
        elif item.value == '∀':
            yield '∈', 'FORALL'
        elif item.value == '∃':
            yield '∈', 'EXIST'
        elif item.value == '∈':
            yield '∈', 'ISIN'
        elif item.value == '∉':
            yield '∈', 'NOTIN'
        else:
            yield '∉', '!KW_NOT|KW_AND|KW_OR'
    elif value == 1:
        if item.value in '\t ':
            yield '∈', 1
            yield '∉', 'WHITESPACE'
        else:
            yield '∉', 'WHITESPACE'
    elif value == 2:
        if item.value == '\n':
            yield '∈', 13
            yield '∉', 'NEWLINE'
        else:
            yield '∉', 'NEWLINE'
    elif value == 3:
        if item.value in '0123456789':
            yield '∈', 14
        else:
            yield '∉', '!FLOAT'
    elif value == 4:
        if item.value == '.':
            yield '∉', 'INT'
            yield '∈', 15
        elif item.value in '0123456789':
            yield '∈', 4
            yield '∉', 'INT'
        else:
            yield '∉', 'INT'
    elif value == 5:
        if item.value == '=':
            yield '∈', 'LV_EQUAL'
            yield '∉', 'LV'
        else:
            yield '∉', 'LV'
    elif value == 6:
        if item.value == '=':
            yield '∉', 'EQUAL'
            yield '∈', 'EQUAL_EQUAL'
        else:
            yield '∉', 'EQUAL'
    elif value == 7:
        if item.value == '=':
            yield '∉', 'RV'
            yield '∈', 'RV_EQUAL'
        else:
            yield '∉', 'RV'
    elif value == 8:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            yield '∈', 8
            yield '∉', 'VAR'
        else:
            yield '∉', 'VAR'
    elif value == 9:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmopqrstuvwxyz':
            yield '∈', 8
            yield '∉', 'VAR'
        elif item.value == 'n':
            yield '∈', 16
            yield '∉', 'VAR'
        else:
            yield '∉', 'VAR'
    elif value == 10:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnpqrstuvwxyz':
            yield '∉', 'VAR'
            yield '∈', 8
        elif item.value == 'o':
            yield '∈', 17
            yield '∉', 'VAR'
        else:
            yield '∉', 'VAR'
    elif value == 11:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqstuvwxyz':
            yield '∈', 8
            yield '∉', 'VAR'
        elif item.value == 'r':
            yield '∈', 18
            yield '∉', 'VAR'
        else:
            yield '∉', 'VAR'
    elif value == 12:
        if item.value in '²³¹⁰⁴⁵⁶⁷⁸⁹':
            yield '∉', 'INT_POW'
            yield '∈', 12
        else:
            yield '∉', 'INT_POW'
    elif value == 13:
        if item.value == '\n':
            yield '∈', 13
            yield '∉', 'NEWLINE'
        else:
            yield '∉', 'NEWLINE'
    elif value == 14:
        if item.value in '0123456789':
            yield '∈', 14
            yield '∉', 'FLOAT'
        else:
            yield '∉', 'FLOAT'
    elif value == 15:
        if item.value == '.':
            yield '∈', 14
        else:
            yield '∉', '!FLOAT'
    elif value == 16:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcefghijklmnopqrstuvwxyz':
            yield '∈', 8
            yield '∉', 'VAR'
        elif item.value == 'd':
            yield '∈', 19
            yield '∉', 'VAR'
        else:
            yield '∉', 'VAR'
    elif value == 17:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrsuvwxyz':
            yield '∉', 'VAR'
            yield '∈', 8
        elif item.value == 't':
            yield '∈', 20
            yield '∉', 'VAR'
        else:
            yield '∉', 'VAR'
    elif value == 18:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            yield '∈', 8
            yield '∉', 'KW_OR'
        else:
            yield '∉', 'KW_OR'
    elif value == 19:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            yield '∈', 8
            yield '∉', 'KW_AND'
        else:
            yield '∉', 'KW_AND'
    elif value == 20:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            yield '∈', 8
            yield '∉', 'KW_NOT'
        else:
            yield '∉', 'KW_NOT'
    else:
        raise Exception(f'\nvalue: {value!r}\nitem: {item!r}')
