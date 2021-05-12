from typing import Iterator, Tuple, Union

__all__ = ['mood_lexer']


def mood_lexer(value: int, item) -> Iterator[Tuple[str, Union[int, str]]]:
    if value == 0:
        if item.value == 'a':
            yield '∈', 1
        else:
            yield '∉', '!PAR|IMP|CON|IND|INF|SUB'
    elif value == 1:
        if item.value == 'b':
            yield '∈', 2
        else:
            yield '∉', '!PAR|IMP|CON|IND|INF|SUB'
    elif value == 2:
        if item.value == 'a':
            yield '∈', 3
        else:
            yield '∉', '!PAR|IMP|CON|IND|INF|SUB'
    elif value == 3:
        if item.value == 'i':
            yield '∈', 4
        else:
            yield '∉', '!PAR|IMP|CON|IND|INF|SUB'
    elif value == 4:
        if item.value == 's':
            yield '∈', 5
        else:
            yield '∉', '!PAR|IMP|CON|IND|INF|SUB'
    elif value == 5:
        if item.value == 's':
            yield '∈', 6
        else:
            yield '∉', '!PAR|IMP|CON|IND|INF|SUB'
    elif value == 6:
        if item.value == 'a':
            yield '∈', 7
        elif item.value == 'e':
            yield '∈', 8
        elif item.value == 'é':
            yield '∈', 9
        else:
            yield '∉', '!PAR|IMP|CON|IND|INF|SUB'
    elif value == 7:
        if item.value == 's':
            yield '∈', 10
        else:
            yield '∉', '!SUB'
    elif value == 8:
        if item.value == 'r':
            yield '∈', 11
        elif item.value == 'z':
            yield '∈', 'IMP'
        else:
            yield '∉', '!CON|IMP|IND|INF'
    elif value == 9:
        if item.value == 'e':
            yield '∈', 12
        else:
            yield '∉', '!PAR'
    elif value == 10:
        if item.value == 's':
            yield '∈', 13
        else:
            yield '∉', '!SUB'
    elif value == 11:
        if item.value == 'a':
            yield '∉', 'INF'
            yield '∈', 14
        elif item.value == 'o':
            yield '∉', 'INF'
            yield '∈', 15
        else:
            yield '∉', 'INF'
    elif value == 12:
        if item.value == 's':
            yield '∈', 'PAR'
        else:
            yield '∉', '!PAR'
    elif value == 13:
        if item.value == 'e':
            yield '∈', 16
        else:
            yield '∉', '!SUB'
    elif value == 14:
        if item.value == 'i':
            yield '∈', 17
        else:
            yield '∉', '!CON'
    elif value == 15:
        if item.value == 'n':
            yield '∈', 18
        else:
            yield '∉', '!IND'
    elif value == 16:
        if item.value == 'n':
            yield '∈', 19
        else:
            yield '∉', '!SUB'
    elif value == 17:
        if item.value == 'e':
            yield '∈', 20
        else:
            yield '∉', '!CON'
    elif value == 18:
        if item.value == 't':
            yield '∈', 'IND'
        else:
            yield '∉', '!IND'
    elif value == 19:
        if item.value == 't':
            yield '∈', 'SUB'
        else:
            yield '∉', '!SUB'
    elif value == 20:
        if item.value == 'n':
            yield '∈', 21
        else:
            yield '∉', '!CON'
    elif value == 21:
        if item.value == 't':
            yield '∈', 'CON'
        else:
            yield '∉', '!CON'
    else:
        raise Exception(f'\nvalue: {value!r}\nitem: {item!r}')
