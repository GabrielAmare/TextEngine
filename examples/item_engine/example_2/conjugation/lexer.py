from typing import Iterator, Tuple, Union

__all__ = ['lexer']


def lexer(value: int, item) -> Iterator[Tuple[str, Union[int, str]]]:
    if value == 0:
        if item.value == 'a':
            yield '∈', 1
        else:
            yield '∉', '!VER-CON-IND-IM-__3SPMF|VER-CON-CON-PR-12_S_MF|VER-CON-SUB-PR-1_3S_MF|VER-CON-PAR-PA-__3S_M_|VER-CON-PAR-PA-__3_PM_|VER-CON-IMP-PR-_2_S_MF|VER-CON-IND-PR-1_3S_MF|VER-CON-IND-IM-12_S_MF|VER-CON-IND-PR-__3SPMF|VER-CON-CON-PR-__3SPMF|VER-CON-IMP-PR-_2__PMF|VER-CON-PAR-PA-__3S__F|VER-CON-IND-FS-__3SPMF|VER-CON-SUB-PR-__3SPMF|VER-CON-INF-PR-__3SPMF|VER-CON-PAR-PR-__3SPMF|VER-CON-PAR-PA-__3_P_F|VER-CON-IMP-PR-1___PMF|VER-CON-SUB-IM-__3SPMF|VER-CON-IND-PS-__3SPMF'
    elif value == 1:
        if item.value == 'b':
            yield '∈', 2
        else:
            yield '∉', '!VER-CON-IND-IM-__3SPMF|VER-CON-CON-PR-12_S_MF|VER-CON-SUB-PR-1_3S_MF|VER-CON-PAR-PA-__3S_M_|VER-CON-PAR-PA-__3_PM_|VER-CON-IMP-PR-_2_S_MF|VER-CON-IND-PR-1_3S_MF|VER-CON-IND-IM-12_S_MF|VER-CON-IND-PR-__3SPMF|VER-CON-CON-PR-__3SPMF|VER-CON-IMP-PR-_2__PMF|VER-CON-PAR-PA-__3S__F|VER-CON-IND-FS-__3SPMF|VER-CON-SUB-PR-__3SPMF|VER-CON-INF-PR-__3SPMF|VER-CON-PAR-PR-__3SPMF|VER-CON-PAR-PA-__3_P_F|VER-CON-IMP-PR-1___PMF|VER-CON-SUB-IM-__3SPMF|VER-CON-IND-PS-__3SPMF'
    elif value == 2:
        if item.value == 'a':
            yield '∈', 3
        else:
            yield '∉', '!VER-CON-IND-IM-__3SPMF|VER-CON-CON-PR-12_S_MF|VER-CON-SUB-PR-1_3S_MF|VER-CON-PAR-PA-__3S_M_|VER-CON-PAR-PA-__3_PM_|VER-CON-IMP-PR-_2_S_MF|VER-CON-IND-PR-1_3S_MF|VER-CON-IND-IM-12_S_MF|VER-CON-IND-PR-__3SPMF|VER-CON-CON-PR-__3SPMF|VER-CON-IMP-PR-_2__PMF|VER-CON-PAR-PA-__3S__F|VER-CON-IND-FS-__3SPMF|VER-CON-SUB-PR-__3SPMF|VER-CON-INF-PR-__3SPMF|VER-CON-PAR-PR-__3SPMF|VER-CON-PAR-PA-__3_P_F|VER-CON-IMP-PR-1___PMF|VER-CON-SUB-IM-__3SPMF|VER-CON-IND-PS-__3SPMF'
    elif value == 3:
        if item.value == 'i':
            yield '∈', 4
        else:
            yield '∉', '!VER-CON-IND-IM-__3SPMF|VER-CON-CON-PR-12_S_MF|VER-CON-SUB-PR-1_3S_MF|VER-CON-PAR-PA-__3S_M_|VER-CON-PAR-PA-__3_PM_|VER-CON-IMP-PR-_2_S_MF|VER-CON-IND-PR-1_3S_MF|VER-CON-IND-IM-12_S_MF|VER-CON-IND-PR-__3SPMF|VER-CON-CON-PR-__3SPMF|VER-CON-PAR-PA-__3S__F|VER-CON-IMP-PR-_2__PMF|VER-CON-IND-FS-__3SPMF|VER-CON-SUB-PR-__3SPMF|VER-CON-INF-PR-__3SPMF|VER-CON-PAR-PR-__3SPMF|VER-CON-PAR-PA-__3_P_F|VER-CON-IMP-PR-1___PMF|VER-CON-SUB-IM-__3SPMF|VER-CON-IND-PS-__3SPMF'
    elif value == 4:
        if item.value == 's':
            yield '∈', 5
        else:
            yield '∉', '!VER-CON-IND-IM-__3SPMF|VER-CON-CON-PR-12_S_MF|VER-CON-SUB-PR-1_3S_MF|VER-CON-PAR-PA-__3S_M_|VER-CON-PAR-PA-__3_PM_|VER-CON-IMP-PR-_2_S_MF|VER-CON-IND-PR-1_3S_MF|VER-CON-IND-IM-12_S_MF|VER-CON-IND-PR-__3SPMF|VER-CON-CON-PR-__3SPMF|VER-CON-PAR-PA-__3S__F|VER-CON-IMP-PR-_2__PMF|VER-CON-IND-FS-__3SPMF|VER-CON-SUB-PR-__3SPMF|VER-CON-INF-PR-__3SPMF|VER-CON-PAR-PR-__3SPMF|VER-CON-PAR-PA-__3_P_F|VER-CON-IMP-PR-1___PMF|VER-CON-SUB-IM-__3SPMF|VER-CON-IND-PS-__3SPMF'
    elif value == 5:
        if item.value == 's':
            yield '∈', 6
        else:
            yield '∉', '!VER-CON-IND-IM-__3SPMF|VER-CON-SUB-PR-1_3S_MF|VER-CON-CON-PR-12_S_MF|VER-CON-PAR-PA-__3S_M_|VER-CON-PAR-PA-__3_PM_|VER-CON-IMP-PR-_2_S_MF|VER-CON-IND-PR-1_3S_MF|VER-CON-IND-IM-12_S_MF|VER-CON-IND-PR-__3SPMF|VER-CON-CON-PR-__3SPMF|VER-CON-PAR-PA-__3S__F|VER-CON-IMP-PR-_2__PMF|VER-CON-IND-FS-__3SPMF|VER-CON-SUB-PR-__3SPMF|VER-CON-INF-PR-__3SPMF|VER-CON-PAR-PR-__3SPMF|VER-CON-PAR-PA-__3_P_F|VER-CON-IMP-PR-1___PMF|VER-CON-SUB-IM-__3SPMF|VER-CON-IND-PS-__3SPMF'
    elif value == 6:
        if item.value == 'a':
            yield '∈', 7
        elif item.value == 'e':
            yield '∈', 8
        elif item.value == 'o':
            yield '∈', 9
        elif item.value == 'è':
            yield '∈', 10
        elif item.value == 'é':
            yield '∈', 11
        else:
            yield '∉', '!VER-CON-IND-IM-__3SPMF|VER-CON-SUB-PR-1_3S_MF|VER-CON-CON-PR-12_S_MF|VER-CON-PAR-PA-__3S_M_|VER-CON-PAR-PA-__3_PM_|VER-CON-IMP-PR-_2_S_MF|VER-CON-IND-PR-1_3S_MF|VER-CON-IND-IM-12_S_MF|VER-CON-IND-PR-__3SPMF|VER-CON-CON-PR-__3SPMF|VER-CON-IMP-PR-_2__PMF|VER-CON-PAR-PA-__3S__F|VER-CON-IND-FS-__3SPMF|VER-CON-SUB-PR-__3SPMF|VER-CON-INF-PR-__3SPMF|VER-CON-PAR-PR-__3SPMF|VER-CON-PAR-PA-__3_P_F|VER-CON-IMP-PR-1___PMF|VER-CON-SUB-IM-__3SPMF|VER-CON-IND-PS-__3SPMF'
    elif value == 7:
        if item.value == 'i':
            yield '∈', 12
        elif item.value == 'n':
            yield '∈', 13
        elif item.value == 's':
            yield '∈', 14
        else:
            yield '∉', '!VER-CON-PAR-PR-__3SPMF|VER-CON-IND-IM-__3SPMF|VER-CON-SUB-IM-__3SPMF|VER-CON-IND-IM-12_S_MF'
    elif value == 8:
        if item.value == 'n':
            yield '∉', 'VER-CON-IND-PR-1_3S_MF'
            yield '∉', 'VER-CON-SUB-PR-1_3S_MF'
            yield '∉', 'VER-CON-IMP-PR-_2_S_MF'
            yield '∈', 15
        elif item.value == 'r':
            yield '∉', 'VER-CON-SUB-PR-1_3S_MF'
            yield '∉', 'VER-CON-IND-PR-1_3S_MF'
            yield '∉', 'VER-CON-IMP-PR-_2_S_MF'
            yield '∈', 16
        elif item.value == 'z':
            yield '∉', 'VER-CON-IND-PR-1_3S_MF'
            yield '∉', 'VER-CON-IMP-PR-_2_S_MF'
            yield '∉', 'VER-CON-SUB-PR-1_3S_MF'
            yield '∈', 'VER-CON-IMP-PR-_2__PMF'
        else:
            yield '∉', 'VER-CON-IND-PR-1_3S_MF'
            yield '∉', 'VER-CON-IMP-PR-_2_S_MF'
            yield '∉', 'VER-CON-SUB-PR-1_3S_MF'
    elif value == 9:
        if item.value == 'n':
            yield '∈', 17
        else:
            yield '∉', '!VER-CON-IMP-PR-1___PMF'
    elif value == 10:
        if item.value == 'r':
            yield '∈', 18
        else:
            yield '∉', '!VER-CON-IND-PS-__3SPMF'
    elif value == 11:
        if item.value == 'e':
            yield '∈', 19
            yield '∉', 'VER-CON-PAR-PA-__3S_M_'
        elif item.value == 's':
            yield '∉', 'VER-CON-PAR-PA-__3S_M_'
            yield '∈', 'VER-CON-PAR-PA-__3_PM_'
        else:
            yield '∉', 'VER-CON-PAR-PA-__3S_M_'
    elif value == 12:
        if item.value == 'e':
            yield '∈', 20
        elif item.value == 's':
            yield '∈', 'VER-CON-IND-IM-12_S_MF'
        else:
            yield '∉', '!VER-CON-IND-IM-__3SPMF|VER-CON-IND-IM-12_S_MF'
    elif value == 13:
        if item.value == 't':
            yield '∈', 'VER-CON-PAR-PR-__3SPMF'
        else:
            yield '∉', '!VER-CON-PAR-PR-__3SPMF'
    elif value == 14:
        if item.value == 's':
            yield '∈', 21
        else:
            yield '∉', '!VER-CON-SUB-IM-__3SPMF'
    elif value == 15:
        if item.value == 't':
            yield '∈', 'VER-CON-SUB-PR-__3SPMF'
            yield '∈', 'VER-CON-IND-PR-__3SPMF'
        else:
            yield '∉', '!VER-CON-SUB-PR-__3SPMF|VER-CON-IND-PR-__3SPMF'
    elif value == 16:
        if item.value == 'a':
            yield '∈', 22
            yield '∉', 'VER-CON-INF-PR-__3SPMF'
        elif item.value == 'o':
            yield '∉', 'VER-CON-INF-PR-__3SPMF'
            yield '∈', 23
        else:
            yield '∉', 'VER-CON-INF-PR-__3SPMF'
    elif value == 17:
        if item.value == 's':
            yield '∈', 'VER-CON-IMP-PR-1___PMF'
        else:
            yield '∉', '!VER-CON-IMP-PR-1___PMF'
    elif value == 18:
        if item.value == 'e':
            yield '∈', 24
        else:
            yield '∉', '!VER-CON-IND-PS-__3SPMF'
    elif value == 19:
        if item.value == 's':
            yield '∉', 'VER-CON-PAR-PA-__3S__F'
            yield '∈', 'VER-CON-PAR-PA-__3_P_F'
        else:
            yield '∉', 'VER-CON-PAR-PA-__3S__F'
    elif value == 20:
        if item.value == 'n':
            yield '∈', 25
        else:
            yield '∉', '!VER-CON-IND-IM-__3SPMF'
    elif value == 21:
        if item.value == 'e':
            yield '∈', 26
        else:
            yield '∉', '!VER-CON-SUB-IM-__3SPMF'
    elif value == 22:
        if item.value == 'i':
            yield '∈', 27
        else:
            yield '∉', '!VER-CON-CON-PR-__3SPMF|VER-CON-CON-PR-12_S_MF'
    elif value == 23:
        if item.value == 'n':
            yield '∈', 28
        else:
            yield '∉', '!VER-CON-IND-FS-__3SPMF'
    elif value == 24:
        if item.value == 'n':
            yield '∈', 29
        else:
            yield '∉', '!VER-CON-IND-PS-__3SPMF'
    elif value == 25:
        if item.value == 't':
            yield '∈', 'VER-CON-IND-IM-__3SPMF'
        else:
            yield '∉', '!VER-CON-IND-IM-__3SPMF'
    elif value == 26:
        if item.value == 'n':
            yield '∈', 30
        else:
            yield '∉', '!VER-CON-SUB-IM-__3SPMF'
    elif value == 27:
        if item.value == 'e':
            yield '∈', 31
        elif item.value == 's':
            yield '∈', 'VER-CON-CON-PR-12_S_MF'
        else:
            yield '∉', '!VER-CON-CON-PR-__3SPMF|VER-CON-CON-PR-12_S_MF'
    elif value == 28:
        if item.value == 't':
            yield '∈', 'VER-CON-IND-FS-__3SPMF'
        else:
            yield '∉', '!VER-CON-IND-FS-__3SPMF'
    elif value == 29:
        if item.value == 't':
            yield '∈', 'VER-CON-IND-PS-__3SPMF'
        else:
            yield '∉', '!VER-CON-IND-PS-__3SPMF'
    elif value == 30:
        if item.value == 't':
            yield '∈', 'VER-CON-SUB-IM-__3SPMF'
        else:
            yield '∉', '!VER-CON-SUB-IM-__3SPMF'
    elif value == 31:
        if item.value == 'n':
            yield '∈', 32
        else:
            yield '∉', '!VER-CON-CON-PR-__3SPMF'
    elif value == 32:
        if item.value == 't':
            yield '∈', 'VER-CON-CON-PR-__3SPMF'
        else:
            yield '∉', '!VER-CON-CON-PR-__3SPMF'
    else:
        raise Exception(f'\nvalue: {value!r}\nitem: {item!r}')
