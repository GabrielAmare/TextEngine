from item_engine import ACTION, STATE
from item_engine.textbase.elements import Char, Token
from typing import Tuple


__all__ = ['lexer']


def lexer(current: Token, item: Char) -> Tuple[ACTION, STATE]:
    if current.value == 0:
        if item.value == '\n':
            return '∈', 2
        elif item.value == '!':
            return '∈', 'EXC'
        elif item.value == '&':
            return '∈', 'AMPS'
        elif item.value == '(':
            return '∈', 'LP'
        elif item.value == ')':
            return '∈', 'RP'
        elif item.value == '*':
            return '∈', 'STAR'
        elif item.value == '+':
            return '∈', 'PLUS'
        elif item.value == ',':
            return '∈', 'COMMA'
        elif item.value == '-':
            return '∈', 'DASH'
        elif item.value == '.':
            return '∈', 3
        elif item.value == '/':
            return '∈', 'SLASH'
        elif item.value == '<':
            return '∈', 5
        elif item.value == '=':
            return '∈', 6
        elif item.value == '>':
            return '∈', 7
        elif item.value == '^':
            return '∈', 'HAT'
        elif item.value == 'a':
            return '∈', 9
        elif item.value == 'n':
            return '∈', 10
        elif item.value == 'o':
            return '∈', 11
        elif item.value == '{':
            return '∈', 'LS'
        elif item.value == '|':
            return '∈', 'VBAR'
        elif item.value == '}':
            return '∈', 'RS'
        elif item.value == '∀':
            return '∈', 'FORALL'
        elif item.value == '∃':
            return '∈', 'EXIST'
        elif item.value == '∈':
            return '∈', 'ISIN'
        elif item.value == '∉':
            return '∈', 'NOTIN'
        elif item.value in '\t ':
            return '∈', 1
        elif item.value in '0123456789':
            return '∈', 4
        elif item.value in '²³¹⁰⁴⁵⁶⁷⁸⁹':
            return '∈', 12
        elif item.value in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_bcdefghijklmpqrstuvwxyz':
            return '∈', 8
        else:
            return '∉', '!KW_AND|KW_NOT'
    elif current.value == 1:
        if item.value in '\t ':
            return '∈', 1
        else:
            return '∉', 'WHITESPACE'
    elif current.value == 2:
        if item.value == '\n':
            return '∈', 13
        else:
            return '∉', 'NEWLINE'
    elif current.value == 3:
        if item.value in '0123456789':
            return '∈', 14
        else:
            return '∉', '!FLOAT'
    elif current.value == 4:
        if item.value == '.':
            return '∈', 14
        elif item.value in '0123456789':
            return '∈', 4
        else:
            return '∉', 'INT'
    elif current.value == 5:
        if item.value == '=':
            return '∉', 'LV'
        else:
            return '∉', 'LV'
    elif current.value == 6:
        if item.value == '=':
            return '∉', 'EQUAL'
        else:
            return '∉', 'EQUAL'
    elif current.value == 7:
        if item.value == '=':
            return '∉', 'RV'
        else:
            return '∉', 'RV'
    elif current.value == 8:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 8
        else:
            return '∉', 'VAR'
    elif current.value == 9:
        if item.value == 'n':
            return '∈', 15
        elif item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmopqrstuvwxyz':
            return '∈', 8
        else:
            return '∉', 'VAR'
    elif current.value == 10:
        if item.value == 'o':
            return '∈', 16
        elif item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnpqrstuvwxyz':
            return '∈', 8
        else:
            return '∉', 'VAR'
    elif current.value == 11:
        if item.value == 'r':
            return '∈', 17
        elif item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqstuvwxyz':
            return '∈', 8
        else:
            return '∉', 'VAR'
    elif current.value == 12:
        if item.value in '²³¹⁰⁴⁵⁶⁷⁸⁹':
            return '∈', 12
        else:
            return '∉', 'INT_POW'
    elif current.value == 13:
        if item.value == '\n':
            return '∈', 13
        else:
            return '∉', 'NEWLINE'
    elif current.value == 14:
        if item.value in '0123456789':
            return '∈', 14
        else:
            return '∉', 'FLOAT'
    elif current.value == 15:
        if item.value == 'd':
            return '∈', 18
        elif item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcefghijklmnopqrstuvwxyz':
            return '∈', 8
        else:
            return '∉', 'VAR'
    elif current.value == 16:
        if item.value == 't':
            return '∈', 19
        elif item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrsuvwxyz':
            return '∈', 8
        else:
            return '∉', 'VAR'
    elif current.value == 17:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 8
        else:
            return '∉', 'KW_OR'
    elif current.value == 18:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 8
        else:
            return '∉', 'KW_AND'
    elif current.value == 19:
        if item.value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz':
            return '∈', 8
        else:
            return '∉', 'KW_NOT'
    else:
        raise Exception(f'value = {current.value!r}')
