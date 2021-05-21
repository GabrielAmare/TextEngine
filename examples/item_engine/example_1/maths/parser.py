from item_engine import ACTION, STATE
from item_engine.textbase.elements import Lemma, Token
from typing import Dict, Iterator, List, Tuple, Union


__all__ = ['parser']


def _parser(current: Lemma, item: Token) -> Iterator[Tuple[ACTION, STATE]]:
    if current.value == 0:
        if item.value == 'DASH':
            yield '∈', 1
        elif item.value == 'EXIST':
            yield '∈', 2
        elif item.value == 'FORALL':
            yield '∈', 5
        elif item.value == 'KW_NOT':
            yield '∈', 6
        elif item.value == 'LP':
            yield '∈', 7
        elif item.value == 'LS':
            yield '∈', 8
        elif item.value == 'VAR':
            yield 'as:c0', 9
            yield 'in:cs', 4
        elif item.value == '__ATTR__':
            yield 'in:cs', 12
        elif item.value == '__FORALL__':
            yield 'as:c0', 15
        elif item.value == '__OR__':
            yield 'as:c0', 16
        elif item.value == '__PAR__':
            yield 'as:c0', 17
            yield 'in:cs', 4
        elif item.value == '__POW__':
            yield 'as:c0', 17
        elif item.value in ('FLOAT', 'INT'):
            yield 'as:c0', 3
            yield 'in:cs', 4
        elif item.value in ('__ADD__', '__SUB__'):
            yield 'as:c0', 10
        elif item.value in ('__AND__', '__NOT__'):
            yield 'as:c0', 11
        elif item.value in ('__DIV__', '__MUL__', '__NEG__'):
            yield 'as:c0', 13
        elif item.value in ('__EQ__', '__GE__', '__GT__', '__LE__', '__LT__'):
            yield 'as:c0', 14
        else:
            yield '∉', '!__ADD__|__AND__|__ATTR__|__CONSTRAINT__|__DIV__|__ENUMV__|__EQUATIONS__|__EQ__|__EXISTS__|__FORALL__|__GE__|__GT__|__LE__|__LT__|__MUL__|__NEG__|__NOT__|__OR__|__PAR__|__POW__|__SET__|__SUB__'
    elif current.value == 1:
        if item.value in ('FLOAT', 'INT', 'VAR', '__NEG__', '__PAR__', '__POW__'):
            yield 'as:c0', '__NEG__'
        else:
            yield '∉', '!__NEG__'
    elif current.value == 2:
        if item.value == 'VAR':
            yield 'as:c0', 18
        else:
            yield '∉', '!__EXISTS__'
    elif current.value == 3:
        if item.value == 'DASH':
            yield '∈', 19
        elif item.value == 'EQUAL_EQUAL':
            yield '∈', 20
        elif item.value == 'HAT':
            yield '∈', 21
        elif item.value == 'INT_POW':
            yield 'as:c1', '__POW__'
        elif item.value == 'KW_AND':
            yield '∈', 22
        elif item.value == 'KW_OR':
            yield '∈', 23
        elif item.value == 'LV':
            yield '∈', 24
        elif item.value == 'LV_EQUAL':
            yield '∈', 25
        elif item.value == 'PLUS':
            yield '∈', 26
        elif item.value == 'RV':
            yield '∈', 27
        elif item.value == 'RV_EQUAL':
            yield '∈', 28
        elif item.value == 'SLASH':
            yield '∈', 29
        elif item.value == 'STAR':
            yield '∈', 30
        elif item.value in ('FLOAT', 'INT', 'VAR', '__PAR__', '__POW__'):
            yield 'as:c1', '__MUL__'
        else:
            yield '∉', '!__ADD__|__AND__|__DIV__|__EQ__|__GE__|__GT__|__LE__|__LT__|__MUL__|__OR__|__POW__|__SUB__'
    elif current.value == 4:
        if item.value == 'COMMA':
            yield '∈', 31
        else:
            yield '∉', '!__ENUMV__'
    elif current.value == 5:
        if item.value == 'VAR':
            yield 'as:c0', 32
        else:
            yield '∉', '!__FORALL__'
    elif current.value == 6:
        if item.value in ('FLOAT', 'INT', 'VAR', '__ADD__', '__DIV__', '__EQ__', '__GE__', '__GT__', '__LE__', '__LT__', '__MUL__', '__NEG__', '__NOT__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:c0', '__NOT__'
        else:
            yield '∉', '!__NOT__'
    elif current.value == 7:
        if item.value in ('FLOAT', 'INT', 'VAR', '__ADD__', '__AND__', '__DIV__', '__EQ__', '__GE__', '__GT__', '__LE__', '__LT__', '__MUL__', '__NEG__', '__NOT__', '__OR__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:c0', 33
        else:
            yield '∉', '!__PAR__'
    elif current.value == 8:
        if item.value == '__ENUMV__':
            yield 'as:c0', 34
        else:
            yield '∉', '!__SET__'
    elif current.value == 9:
        if item.value == 'DASH':
            yield '∈', 19
        elif item.value == 'EQUAL':
            yield '∈', 35
        elif item.value == 'EQUAL_EQUAL':
            yield '∈', 20
        elif item.value == 'HAT':
            yield '∈', 21
        elif item.value == 'INT_POW':
            yield 'as:c1', '__POW__'
        elif item.value == 'KW_AND':
            yield '∈', 22
        elif item.value == 'KW_OR':
            yield '∈', 23
        elif item.value == 'LV':
            yield '∈', 24
        elif item.value == 'LV_EQUAL':
            yield '∈', 25
        elif item.value == 'PLUS':
            yield '∈', 26
        elif item.value == 'RV':
            yield '∈', 27
        elif item.value == 'RV_EQUAL':
            yield '∈', 28
        elif item.value == 'SLASH':
            yield '∈', 29
        elif item.value == 'STAR':
            yield '∈', 30
        else:
            yield '∉', '!__ADD__|__AND__|__ATTR__|__DIV__|__EQ__|__GE__|__GT__|__LE__|__LT__|__MUL__|__OR__|__POW__|__SUB__'
    elif current.value == 10:
        if item.value == 'DASH':
            yield '∈', 19
        elif item.value == 'EQUAL_EQUAL':
            yield '∈', 20
        elif item.value == 'KW_AND':
            yield '∈', 22
        elif item.value == 'KW_OR':
            yield '∈', 23
        elif item.value == 'LV':
            yield '∈', 24
        elif item.value == 'LV_EQUAL':
            yield '∈', 25
        elif item.value == 'PLUS':
            yield '∈', 26
        elif item.value == 'RV':
            yield '∈', 27
        elif item.value == 'RV_EQUAL':
            yield '∈', 28
        else:
            yield '∉', '!__ADD__|__AND__|__EQ__|__GE__|__GT__|__LE__|__LT__|__OR__|__SUB__'
    elif current.value == 11:
        if item.value == 'KW_AND':
            yield '∈', 22
        elif item.value == 'KW_OR':
            yield '∈', 23
        else:
            yield '∉', '!__AND__|__OR__'
    elif current.value == 12:
        if item.value == 'NEWLINE':
            yield '∈', 36
        else:
            yield '∉', '!__EQUATIONS__'
    elif current.value == 13:
        if item.value == 'DASH':
            yield '∈', 19
        elif item.value == 'EQUAL_EQUAL':
            yield '∈', 20
        elif item.value == 'KW_AND':
            yield '∈', 22
        elif item.value == 'KW_OR':
            yield '∈', 23
        elif item.value == 'LV':
            yield '∈', 24
        elif item.value == 'LV_EQUAL':
            yield '∈', 25
        elif item.value == 'PLUS':
            yield '∈', 26
        elif item.value == 'RV':
            yield '∈', 27
        elif item.value == 'RV_EQUAL':
            yield '∈', 28
        elif item.value == 'SLASH':
            yield '∈', 29
        elif item.value == 'STAR':
            yield '∈', 30
        else:
            yield '∉', '!__ADD__|__AND__|__DIV__|__EQ__|__GE__|__GT__|__LE__|__LT__|__MUL__|__OR__|__SUB__'
    elif current.value == 14:
        if item.value == 'EQUAL_EQUAL':
            yield '∈', 20
        elif item.value == 'KW_AND':
            yield '∈', 22
        elif item.value == 'KW_OR':
            yield '∈', 23
        elif item.value == 'LV':
            yield '∈', 24
        elif item.value == 'LV_EQUAL':
            yield '∈', 25
        elif item.value == 'RV':
            yield '∈', 27
        elif item.value == 'RV_EQUAL':
            yield '∈', 28
        else:
            yield '∉', '!__AND__|__EQ__|__GE__|__GT__|__LE__|__LT__|__OR__'
    elif current.value == 15:
        if item.value == 'COMMA':
            yield '∈', 37
        else:
            yield '∉', '!__CONSTRAINT__'
    elif current.value == 16:
        if item.value == 'KW_OR':
            yield '∈', 23
        else:
            yield '∉', '!__OR__'
    elif current.value == 17:
        if item.value == 'DASH':
            yield '∈', 19
        elif item.value == 'EQUAL_EQUAL':
            yield '∈', 20
        elif item.value == 'HAT':
            yield '∈', 21
        elif item.value == 'INT_POW':
            yield 'as:c1', '__POW__'
        elif item.value == 'KW_AND':
            yield '∈', 22
        elif item.value == 'KW_OR':
            yield '∈', 23
        elif item.value == 'LV':
            yield '∈', 24
        elif item.value == 'LV_EQUAL':
            yield '∈', 25
        elif item.value == 'PLUS':
            yield '∈', 26
        elif item.value == 'RV':
            yield '∈', 27
        elif item.value == 'RV_EQUAL':
            yield '∈', 28
        elif item.value == 'SLASH':
            yield '∈', 29
        elif item.value == 'STAR':
            yield '∈', 30
        else:
            yield '∉', '!__ADD__|__AND__|__DIV__|__EQ__|__GE__|__GT__|__LE__|__LT__|__MUL__|__OR__|__POW__|__SUB__'
    elif current.value == 18:
        if item.value == 'ISIN':
            yield '∈', 38
        else:
            yield '∉', '!__EXISTS__'
    elif current.value == 19:
        if item.value in ('FLOAT', 'INT', 'VAR', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__'):
            yield 'as:c1', '__SUB__'
        else:
            yield '∉', '!__SUB__'
    elif current.value == 20:
        if item.value in ('FLOAT', 'INT', 'VAR', '__ADD__', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:c1', '__EQ__'
        else:
            yield '∉', '!__EQ__'
    elif current.value == 21:
        if item.value in ('FLOAT', 'INT', 'VAR', '__PAR__'):
            yield 'as:c1', '__POW__'
        else:
            yield '∉', '!__POW__'
    elif current.value == 22:
        if item.value in ('FLOAT', 'INT', 'VAR', '__ADD__', '__DIV__', '__EQ__', '__GE__', '__GT__', '__LE__', '__LT__', '__MUL__', '__NEG__', '__NOT__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:c1', '__AND__'
        else:
            yield '∉', '!__AND__'
    elif current.value == 23:
        if item.value in ('FLOAT', 'INT', 'VAR', '__ADD__', '__AND__', '__DIV__', '__EQ__', '__GE__', '__GT__', '__LE__', '__LT__', '__MUL__', '__NEG__', '__NOT__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:c1', '__OR__'
        else:
            yield '∉', '!__OR__'
    elif current.value == 24:
        if item.value in ('FLOAT', 'INT', 'VAR', '__ADD__', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:c1', '__LT__'
        else:
            yield '∉', '!__LT__'
    elif current.value == 25:
        if item.value in ('FLOAT', 'INT', 'VAR', '__ADD__', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:c1', '__LE__'
        else:
            yield '∉', '!__LE__'
    elif current.value == 26:
        if item.value in ('FLOAT', 'INT', 'VAR', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__'):
            yield 'as:c1', '__ADD__'
        else:
            yield '∉', '!__ADD__'
    elif current.value == 27:
        if item.value in ('FLOAT', 'INT', 'VAR', '__ADD__', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:c1', '__GT__'
        else:
            yield '∉', '!__GT__'
    elif current.value == 28:
        if item.value in ('FLOAT', 'INT', 'VAR', '__ADD__', '__DIV__', '__MUL__', '__NEG__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:c1', '__GE__'
        else:
            yield '∉', '!__GE__'
    elif current.value == 29:
        if item.value in ('FLOAT', 'INT', 'VAR', '__NEG__', '__PAR__', '__POW__'):
            yield 'as:c1', '__DIV__'
        else:
            yield '∉', '!__DIV__'
    elif current.value == 30:
        if item.value in ('FLOAT', 'INT', 'VAR', '__NEG__', '__PAR__', '__POW__'):
            yield 'as:c1', '__MUL__'
        else:
            yield '∉', '!__MUL__'
    elif current.value == 31:
        if item.value in ('FLOAT', 'INT', 'VAR', '__PAR__'):
            yield 'in:cs', 39
        else:
            yield '∉', '!__ENUMV__'
    elif current.value == 32:
        if item.value == 'ISIN':
            yield '∈', 40
        else:
            yield '∉', '!__FORALL__'
    elif current.value == 33:
        if item.value == 'RP':
            yield '∈', '__PAR__'
        else:
            yield '∉', '!__PAR__'
    elif current.value == 34:
        if item.value == 'RS':
            yield '∈', '__SET__'
        else:
            yield '∉', '!__SET__'
    elif current.value == 35:
        if item.value in ('FLOAT', 'INT', 'VAR', '__ADD__', '__AND__', '__DIV__', '__EQ__', '__GE__', '__GT__', '__LE__', '__LT__', '__MUL__', '__NEG__', '__NOT__', '__OR__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:c1', '__ATTR__'
        else:
            yield '∉', '!__ATTR__'
    elif current.value == 36:
        if item.value == '__ATTR__':
            yield 'in:cs', 41
        else:
            yield '∉', '!__EQUATIONS__'
    elif current.value == 37:
        if item.value == '__EXISTS__':
            yield 'as:c1', 42
        else:
            yield '∉', '!__CONSTRAINT__'
    elif current.value == 38:
        if item.value == 'VAR':
            yield 'as:c1', '__EXISTS__'
        else:
            yield '∉', '!__EXISTS__'
    elif current.value == 39:
        if item.value == 'COMMA':
            yield '∈', 31
        else:
            yield '∉', '__ENUMV__'
    elif current.value == 40:
        if item.value == 'VAR':
            yield 'as:c1', '__FORALL__'
        else:
            yield '∉', '!__FORALL__'
    elif current.value == 41:
        if item.value == 'NEWLINE':
            yield '∈', 36
        else:
            yield '∉', '__EQUATIONS__'
    elif current.value == 42:
        if item.value == 'VBAR':
            yield '∈', 43
        else:
            yield '∉', '!__CONSTRAINT__'
    elif current.value == 43:
        if item.value in ('FLOAT', 'INT', 'VAR', '__ADD__', '__AND__', '__DIV__', '__EQ__', '__GE__', '__GT__', '__LE__', '__LT__', '__MUL__', '__NEG__', '__NOT__', '__OR__', '__PAR__', '__POW__', '__SUB__'):
            yield 'as:c2', '__CONSTRAINT__'
        else:
            yield '∉', '!__CONSTRAINT__'
    else:
        raise Exception(f'value = {current.value!r}')


def parser(src: Iterator[Token]) -> Iterator[Lemma]:
    curs: Dict[int, List[Lemma]] = {}
    def add_cur(cur: Lemma):
        to = cur.to
        if to not in curs:
            curs[to] = [cur]
        elif cur not in curs[to]:
            curs[to].append(cur)
    
    add_cur(Lemma(at=0, to=0, value=0))
    stack: List[Union[Token, Lemma]] = []
    j: int = 0
    for old in src:
        stack.append(old)
        while j < len(stack):
            oldr: Lemma = stack[j]
            j += 1
            if oldr.at in curs:
                queue = curs[oldr.at]
                add_cur(Lemma(at=oldr.at, to=oldr.at, value=0))
                i = 0
                while i < len(queue):
                    cur: Lemma = queue[i]
                    i += 1
                    for new in (cur.develop(res, oldr) for res in _parser(cur, oldr)):
                        if not new.is_terminal:
                            add_cur(new)
                            continue
                        if new.is_valid:
                            if new not in stack:
                                stack.insert(j, new)
                            add_cur(Lemma(at=new.to, to=new.to, value=0))
                            yield new
                            continue
                continue
        if old.value == 'EOF':
            yield Lemma.EOF(old.to)
            break
