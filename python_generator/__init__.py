import os
from typing import Optional, List, Union

__all__ = (
    "CODE",
    "RAW", "LINES",
    "IF",
    "RETURN", "YIELD", "RAISE",
    "SWITCH",
    "ARGS",
    "DEF",
    "EXCEPTION",
    "STR", "LIST",
    "CONDITION", "EQ", "NE", "IN", "NOT_IN", "LT", "LE", "GT", "GE",
    "MODULE"
)


def indent(text) -> str:
    if isinstance(text, str):
        return "\n".join("    " + line for line in text.split("\n"))
    else:
        return indent(str(text))


class CODE:
    def __str__(self):
        raise NotImplementedError


C = Union[CODE, str]
INLINE = Union[CODE, str]


class CONDITION(CODE):
    pass


class SYMBOL_CONDITION(CONDITION):
    symbol: str

    def __init__(self, left: INLINE, right: INLINE):
        self.left = left
        self.right = right

    def __str__(self):
        return f"{self.left!s} {self.__class__.symbol} {self.right!s}"


class EQ(SYMBOL_CONDITION):
    symbol = '=='


class NE(SYMBOL_CONDITION):
    symbol = '!='


class LT(SYMBOL_CONDITION):
    symbol = '<'


class LE(SYMBOL_CONDITION):
    symbol = '<='


class GT(SYMBOL_CONDITION):
    symbol = '>'


class GE(SYMBOL_CONDITION):
    symbol = '>='


class IN(SYMBOL_CONDITION):
    symbol = 'in'


class NOT_IN(SYMBOL_CONDITION):
    symbol = 'not in'


class RAW(CODE):
    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return self.content


class LINES(CODE):
    def __init__(self, lines: List[C]):
        self.lines = lines

    def __str__(self):
        return "\n".join(map(str, self.lines))


class IF(CODE):
    def __init__(self, cond: CONDITION, body: C):
        self.cond = cond
        self.body = body

    def __str__(self):
        return f"if {self.cond!s}:\n{indent(self.body)}"


class RETURN(CODE):
    def __init__(self, line: INLINE):
        self.line = line

    def __str__(self):
        return f"return {self.line!s}"


class YIELD(CODE):
    def __init__(self, line: INLINE):
        self.line = line

    def __str__(self):
        return f"yield {self.line!s}"


class RAISE(CODE):
    def __init__(self, line: INLINE):
        self.line = line

    def __str__(self):
        return f"raise {self.line!s}"


class EXCEPTION(CODE):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return f"Exception({self.msg!s})"


class SWITCH(CODE):
    def __init__(self, ifs: List[IF], default: Optional[C] = None):
        self.ifs = ifs
        self.default = default

    def __str__(self):
        return "\nel".join(map(str, self.ifs)) + ("" if self.default is None else f"\nelse:\n{indent(self.default)}")


class ARGS:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return ", ".join(list(map(str, self.args)) + [f"{key}={val}" for key, val in self.kwargs])


class FROM_IMPORT:
    def __init__(self, from_: INLINE, args: Union[str, ARGS]):
        self.from_ = from_
        self.args = args

    def __str__(self):
        return f"from {self.from_!s} import {self.args!s}"


class STR:
    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return repr(self.content)


class LIST:
    def __init__(self, elements: List[C]):
        self.elements = elements

    def __str__(self):
        return f"[{', '.join(map(str, self.elements))}]"


class TUPLE:
    def __init__(self, elements: List[C]):
        self.elements = elements

    def __str__(self):
        return f"({', '.join(map(str, self.elements))}{',' if len(self.elements) == 1 else ''})"


class DEF(CODE):
    def __init__(self, name: str, args: ARGS, body: C, type_: str = ""):
        self.name = name
        self.args = args
        self.body = body
        self.type = type_

    def __str__(self):
        return f"def {self.name!s}({self.args!s}){f' -> {self.type}' if self.type else ''}:\n{indent(self.body)}"


class MODULE(CODE):
    def __init__(self, items: List[CODE]):
        self.items = items

    def __str__(self):
        content = ""
        prefix = ""
        for item in self.items:
            content += prefix
            prefix = ""
            if isinstance(item, DEF):
                prefix = "\n\n\n"
            else:
                prefix = "\n\n\n"

            content += f"{item!s}"

        return content + "\n"

    def save(self, fp: str, overwrite: bool = False):
        if not fp.endswith(".py"):
            fp += ".py"

        if os.path.exists(fp) and not overwrite:
            raise FileExistsError(fp)

        with open(fp, mode="w", encoding="utf-8") as file:
            file.write(str(self))
