from typing import Iterator, Tuple, Union

__all__ = ['parser']


def parser(value: int, item) -> Iterator[Tuple[str, Union[int, str]]]:
    if value == 0:
        if item.value == 'DASH':
            yield '∈', 1
        elif item.value == 'EXIST':
            yield '∈', 2
        elif item.value == 'FORALL':
            yield '∈', 3
        elif item.value == 'INT':
            yield 'as:as:c0', 4
            yield 'in:cs', 5
            yield 'as:c0', 6
        elif item.value == 'KW_NOT':
            yield '∈', 7
        elif item.value == 'LP':
            yield '∈', 8
        elif item.value == 'LS':
            yield '∈', 9
        elif item.value == 'VAR':
            yield 'as:as:c0', 10
            yield 'in:cs', 5
            yield 'as:c0', 11
        elif item.value in ('__ADD__', '__SUB__'):
            yield 'as:as:c0', 12
        elif item.value in ('__AND__', '__NOT__'):
            yield 'as:as:c0', 13
        elif item.value == '__ATTR__':
            yield 'in:cs', 14
        elif item.value in ('__DIV__', '__MUL__', '__NEG__'):
            yield 'as:as:c0', 15
        elif item.value in ('__EQ__', '__GE__', '__GT__', '__LE__', '__LT__'):
            yield 'as:as:c0', 16
        elif item.value == '__FORALL__':
            yield 'as:as:c0', 17
        elif item.value == '__OR__':
            yield 'as:as:c0', 18
        elif item.value == '__PAR__':
            yield 'as:as:c0', 4
            yield 'in:cs', 5
        elif item.value == '__POW__':
            yield 'as:as:c0', 4
        else:
            yield '∉', '!__SUB__|__FORALL__|__EQ__|__OR__|__MUL__|__LT__|__EQUATIONS__|__POW__|__DIV__|__AND__|__NOT__|__ATTR__|__NEG__|__GT__|__ADD__|__ENUMV__|__GE__|__PAR__|__CONSTRAINT__|__EXISTS__|__LE__|__SET__'
    elif value == 1:
        if item.value in ('INT', 'VAR', '__NEG__', '__PAR__', '__POW__'):
            yield 'as:as:c0', '__NEG__'
        else:
            yield '∉', '!__NEG__'
    elif value == 2:
        if item.value == 'VAR':
            yield 'as:as:c0', 19
        else:
            yield '∉', '!__EXISTS__'
    elif value == 3:
        if item.value == 'VAR':
            yield 'as:as:c0', 20
        else:
            yield '∉', '!__FORALL__'
    elif value == 4:
        if item.value == 'DASH':
            yield '∈', 21
        elif item.value == 'EQUAL_EQUAL':
            yield '∈', 22
        elif item.value == 'HAT':
            yield '∈', 23
        elif item.value == 'KW_AND':
            yield '∈', 24
        elif item.value == 'KW_OR':
            yield '∈', 25
        elif item.value == 'LV':
            yield '∈', 26
        elif item.value == 'LV_EQUAL':
            yield '∈', 27
        elif item.value == 'PLUS':
            yield '∈', 28
        elif item.value == 'RV':
            yield '∈', 29
        elif item.value == 'RV_EQUAL':
            yield '∈', 30
        elif item.value == 'SLASH':
            yield '∈', 31
        elif item.value == 'STAR':
            yield '∈', 32
        else:
            yield '∉', '!__SUB__|__GT__|__EQ__|__ADD__|__OR__|__MUL__|__GE__|__LT__|__DIV__|__POW__|__AND__|__LE__'
    elif value == 5:
        if item.value == 'COMMA':
            yield '∈', 33
        else:
            yield '∉', '!__ENUMV__'
    elif value == 6:
        if item.value == 'VAR':
            yield 'as:c1', '__MUL__'
        else:
            yield '∉', '!__MUL__'
    elif value == 7:
        if item.value in ('INT', 'VAR', '__ADD__', '__DIV__', '__EQ__', '__GE__', '__GT__', '__LE__', '__LT__', '__MUL__', '__NEG__', '__NOT__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:as:c0', '__NOT__'
        else:
            yield '∉', '!__NOT__'
    elif value == 8:
        if item.value in ('INT', 'VAR', '__ADD__', '__AND__', '__DIV__', '__EQ__', '__GE__', '__GT__', '__LE__', '__LT__', '__MUL__', '__NEG__', '__NOT__', '__OR__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:as:c0', 34
        else:
            yield '∉', '!__PAR__'
    elif value == 9:
        if item.value == '__ENUMV__':
            yield 'as:as:c0', 35
        else:
            yield '∉', '!__SET__'
    elif value == 10:
        if item.value == 'DASH':
            yield '∈', 21
        elif item.value == 'EQUAL':
            yield '∈', 36
        elif item.value == 'EQUAL_EQUAL':
            yield '∈', 22
        elif item.value == 'HAT':
            yield '∈', 23
        elif item.value == 'KW_AND':
            yield '∈', 24
        elif item.value == 'KW_OR':
            yield '∈', 25
        elif item.value == 'LV':
            yield '∈', 26
        elif item.value == 'LV_EQUAL':
            yield '∈', 27
        elif item.value == 'PLUS':
            yield '∈', 28
        elif item.value == 'RV':
            yield '∈', 29
        elif item.value == 'RV_EQUAL':
            yield '∈', 30
        elif item.value == 'SLASH':
            yield '∈', 31
        elif item.value == 'STAR':
            yield '∈', 32
        else:
            yield '∉', '!__SUB__|__GT__|__EQ__|__ADD__|__OR__|__MUL__|__GE__|__LT__|__DIV__|__POW__|__AND__|__LE__|__ATTR__'
    elif value == 11:
        if item.value == 'INT_POW':
            yield 'as:c1', '__POW__'
        else:
            yield '∉', '!__POW__'
    elif value == 12:
        if item.value == 'DASH':
            yield '∈', 21
        elif item.value == 'EQUAL_EQUAL':
            yield '∈', 22
        elif item.value == 'KW_AND':
            yield '∈', 24
        elif item.value == 'KW_OR':
            yield '∈', 25
        elif item.value == 'LV':
            yield '∈', 26
        elif item.value == 'LV_EQUAL':
            yield '∈', 27
        elif item.value == 'PLUS':
            yield '∈', 28
        elif item.value == 'RV':
            yield '∈', 29
        elif item.value == 'RV_EQUAL':
            yield '∈', 30
        else:
            yield '∉', '!__SUB__|__GT__|__EQ__|__ADD__|__OR__|__GE__|__LT__|__AND__|__LE__'
    elif value == 13:
        if item.value == 'KW_AND':
            yield '∈', 24
        elif item.value == 'KW_OR':
            yield '∈', 25
        else:
            yield '∉', '!__OR__|__AND__'
    elif value == 14:
        if item.value == 'NEWLINE':
            yield '∈', 37
        else:
            yield '∉', '!__EQUATIONS__'
    elif value == 15:
        if item.value == 'DASH':
            yield '∈', 21
        elif item.value == 'EQUAL_EQUAL':
            yield '∈', 22
        elif item.value == 'KW_AND':
            yield '∈', 24
        elif item.value == 'KW_OR':
            yield '∈', 25
        elif item.value == 'LV':
            yield '∈', 26
        elif item.value == 'LV_EQUAL':
            yield '∈', 27
        elif item.value == 'PLUS':
            yield '∈', 28
        elif item.value == 'RV':
            yield '∈', 29
        elif item.value == 'RV_EQUAL':
            yield '∈', 30
        elif item.value == 'SLASH':
            yield '∈', 31
        elif item.value == 'STAR':
            yield '∈', 32
        else:
            yield '∉', '!__SUB__|__GT__|__EQ__|__ADD__|__OR__|__MUL__|__GE__|__LT__|__DIV__|__AND__|__LE__'
    elif value == 16:
        if item.value == 'EQUAL_EQUAL':
            yield '∈', 22
        elif item.value == 'KW_AND':
            yield '∈', 24
        elif item.value == 'KW_OR':
            yield '∈', 25
        elif item.value == 'LV':
            yield '∈', 26
        elif item.value == 'LV_EQUAL':
            yield '∈', 27
        elif item.value == 'RV':
            yield '∈', 29
        elif item.value == 'RV_EQUAL':
            yield '∈', 30
        else:
            yield '∉', '!__GT__|__EQ__|__AND__|__OR__|__LE__|__LT__|__GE__'
    elif value == 17:
        if item.value == 'COMMA':
            yield '∈', 38
        else:
            yield '∉', '!__CONSTRAINT__'
    elif value == 18:
        if item.value == 'KW_OR':
            yield '∈', 25
        else:
            yield '∉', '!__OR__'
    elif value == 19:
        if item.value == 'ISIN':
            yield '∈', 39
        else:
            yield '∉', '!__EXISTS__'
    elif value == 20:
        if item.value == 'ISIN':
            yield '∈', 40
        else:
            yield '∉', '!__FORALL__'
    elif value == 21:
        if item.value in ('INT', 'VAR', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__'):
            yield 'as:as:c1', '__SUB__'
        else:
            yield '∉', '!__SUB__'
    elif value == 22:
        if item.value in ('INT', 'VAR', '__ADD__', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:as:c1', '__EQ__'
        else:
            yield '∉', '!__EQ__'
    elif value == 23:
        if item.value in ('INT', 'VAR', '__PAR__'):
            yield 'as:as:c1', '__POW__'
        else:
            yield '∉', '!__POW__'
    elif value == 24:
        if item.value in ('INT', 'VAR', '__ADD__', '__DIV__', '__EQ__', '__GE__', '__GT__', '__LE__', '__LT__', '__MUL__', '__NEG__', '__NOT__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:as:c1', '__AND__'
        else:
            yield '∉', '!__AND__'
    elif value == 25:
        if item.value in ('INT', 'VAR', '__ADD__', '__AND__', '__DIV__', '__EQ__', '__GE__', '__GT__', '__LE__', '__LT__', '__MUL__', '__NEG__', '__NOT__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:as:c1', '__OR__'
        else:
            yield '∉', '!__OR__'
    elif value == 26:
        if item.value in ('INT', 'VAR', '__ADD__', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:as:c1', '__LT__'
        else:
            yield '∉', '!__LT__'
    elif value == 27:
        if item.value in ('INT', 'VAR', '__ADD__', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:as:c1', '__LE__'
        else:
            yield '∉', '!__LE__'
    elif value == 28:
        if item.value in ('INT', 'VAR', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__'):
            yield 'as:as:c1', '__ADD__'
        else:
            yield '∉', '!__ADD__'
    elif value == 29:
        if item.value in ('INT', 'VAR', '__ADD__', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:as:c1', '__GT__'
        else:
            yield '∉', '!__GT__'
    elif value == 30:
        if item.value in ('INT', 'VAR', '__ADD__', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:as:c1', '__GE__'
        else:
            yield '∉', '!__GE__'
    elif value == 31:
        if item.value in ('INT', 'VAR', '__NEG__', '__PAR__', '__POW__'):
            yield 'as:as:c1', '__DIV__'
        else:
            yield '∉', '!__DIV__'
    elif value == 32:
        if item.value in ('INT', 'VAR', '__NEG__', '__PAR__', '__POW__'):
            yield 'as:as:c1', '__MUL__'
        else:
            yield '∉', '!__MUL__'
    elif value == 33:
        if item.value in ('INT', 'VAR', '__PAR__'):
            yield 'in:cs', 41
        else:
            yield '∉', '!__ENUMV__'
    elif value == 34:
        if item.value == 'RP':
            yield '∈', '__PAR__'
        else:
            yield '∉', '!__PAR__'
    elif value == 35:
        if item.value == 'RS':
            yield '∈', '__SET__'
        else:
            yield '∉', '!__SET__'
    elif value == 36:
        if item.value in ('INT', 'VAR', '__ADD__', '__AND__', '__DIV__', '__EQ__', '__GE__', '__GT__', '__LE__', '__LT__', '__MUL__', '__NEG__', '__NOT__', '__OR__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:as:c1', '__ATTR__'
        else:
            yield '∉', '!__ATTR__'
    elif value == 37:
        if item.value == '__ATTR__':
            yield 'in:cs', 42
        else:
            yield '∉', '!__EQUATIONS__'
    elif value == 38:
        if item.value == '__EXISTS__':
            yield 'as:as:c1', 43
        else:
            yield '∉', '!__CONSTRAINT__'
    elif value == 39:
        if item.value == 'VAR':
            yield 'as:as:c1', '__EXISTS__'
        else:
            yield '∉', '!__EXISTS__'
    elif value == 40:
        if item.value == 'VAR':
            yield 'as:as:c1', '__FORALL__'
        else:
            yield '∉', '!__FORALL__'
    elif value == 41:
        if item.value == 'COMMA':
            yield '∈', 33
            yield '∉', '__ENUMV__'
        else:
            yield '∉', '__ENUMV__'
    elif value == 42:
        if item.value == 'NEWLINE':
            yield '∉', '__EQUATIONS__'
            yield '∈', 37
        else:
            yield '∉', '__EQUATIONS__'
    elif value == 43:
        if item.value == 'VBAR':
            yield '∈', 44
        else:
            yield '∉', '!__CONSTRAINT__'
    elif value == 44:
        if item.value in ('INT', 'VAR', '__ADD__', '__AND__', '__DIV__', '__EQ__', '__GE__', '__GT__', '__LE__', '__LT__', '__MUL__', '__NEG__', '__NOT__', '__OR__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:as:c2', '__CONSTRAINT__'
        else:
            yield '∉', '!__CONSTRAINT__'
    else:
        raise Exception(f'\nvalue: {value!r}\nitem: {item!r}')
