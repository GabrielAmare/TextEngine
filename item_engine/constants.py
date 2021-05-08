from typing import Union

__all__ = [
    "NT_STATE", "T_STATE", "STATE",
    "INDEX", "POSITION",
    "ACTION", "INCLUDE", "EXCLUDE", "AS", "IN"
]

ACTION = str
NT_STATE = int
T_STATE = str
STATE = Union[NT_STATE, T_STATE]

INDEX = int
POSITION = int

INCLUDE: ACTION = "include"
EXCLUDE: ACTION = "exclude"
AS: ACTION = "as:{}"
IN: ACTION = "in:{}"
