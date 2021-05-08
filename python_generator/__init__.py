import os
from dataclasses import dataclass
from typing import Optional, List, Union, Dict

__all__ = [
    "CODE",
    "RAW", "LINES",
    "IF",
    "RETURN", "YIELD", "RAISE",
    "SWITCH",
    "ARGS",
    "DEF", "CALL", "CLASS",
    "EXCEPTION",
    "STR", "FSTR", "LIST",
    "SETATTR",
    "CONDITION", "EQ", "NE", "IN", "NOT_IN", "LT", "LE", "GT", "GE", "ISINSTANCE",
    "MODULE", "PACKAGE",
    "LAMBDA",
    "METHODS"
]


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


@dataclass
class ISINSTANCE(CONDITION):
    o: INLINE
    t: INLINE

    def __str__(self):
        return f"isinstance({self.o!s}, {self.t!s})"


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


@dataclass
class RAW(CODE):
    content: str

    def __str__(self):
        return self.content


@dataclass
class LINES(CODE):
    lines: List[C]

    def __str__(self):
        r = ""
        prefix = ""
        for line in self.lines:
            r += prefix
            r += str(line)
            if isinstance(line, DEF):
                prefix = "\n\n"
            else:
                prefix = "\n"
        return r

        # return "\n".join(map(str, self.lines))


@dataclass
class IF(CODE):
    cond: CONDITION
    body: C

    def __str__(self):
        return f"if {self.cond!s}:\n{indent(self.body)}"


@dataclass
class RETURN(CODE):
    line: INLINE

    def __str__(self):
        return f"return {self.line!s}"


@dataclass
class YIELD(CODE):
    line: INLINE

    def __str__(self):
        return f"yield {self.line!s}"


@dataclass
class RAISE(CODE):
    line: INLINE

    def __str__(self):
        return f"raise {self.line!s}"


@dataclass
class EXCEPTION(CODE):
    msg: INLINE

    def __str__(self):
        return f"Exception({self.msg!s})"


@dataclass
class SWITCH(CODE):
    ifs: List[IF]
    default: Optional[C] = None

    def __str__(self):
        return "\nel".join(map(str, self.ifs)) + ("" if self.default is None else f"\nelse:\n{indent(self.default)}")


class ARGS(CODE):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return ", ".join(list(map(str, self.args)) + [f"{key}={val}" for key, val in self.kwargs])


@dataclass
class ARG(CODE):
    k: str
    v: Optional[INLINE] = None
    t: Optional[str] = None

    # assert k.isidentifier()

    def __str__(self):
        return f"{self.k!s}" + \
               ("" if self.t is None else f": {self.t!s}") + \
               ("" if self.v is None else f"={self.v!s}")


@dataclass
class AS_KWARG(CODE):
    value: INLINE

    def __str__(self):
        return f"**{self.value!s}"


@dataclass
class AS_ARG(CODE):
    value: INLINE

    def __str__(self):
        return f"*{self.value!s}"


@dataclass
class FROM_IMPORT(CODE):
    from_: INLINE
    args: Union[str, ARGS]

    def __str__(self):
        return f"from {self.from_!s} import {self.args!s}"


@dataclass
class STR(CODE):
    content: str

    def __str__(self):
        return repr(self.content)


@dataclass
class FSTR(CODE):
    content: str

    def __str__(self):
        return f'f{self.content!r}'


@dataclass
class LIST(CODE):
    elements: List[C]

    def __str__(self):
        return f"[{', '.join(map(str, self.elements))}]"


@dataclass
class DICT(CODE):
    data: dict

    def __str__(self):
        return '{' + ', '.join(f"{k!r}: {v!r}" for k, v in self.data.items()) + '}'


@dataclass
class TUPLE(CODE):
    elements: List[C]

    def __str__(self):
        return f"({', '.join(map(str, self.elements))}{',' if len(self.elements) == 1 else ''})"


@dataclass
class DEF(CODE):
    name: str
    args: ARGS
    body: C
    type: str = ""

    def __str__(self):
        return f"def {self.name!s}({self.args!s}){f' -> {self.type}' if self.type else ''}:\n{indent(self.body)}"


@dataclass
class CLASS(CODE):
    name: str
    body: C
    herits: Optional[ARGS] = None

    def __str__(self):
        return f"class {self.name!s}{f'({self.herits!s})' if self.herits else ''}:\n{indent(self.body)}"


@dataclass
class CALL(CODE):
    name: str
    args: ARGS

    def __str__(self):
        return f"{self.name!s}({self.args!s})"


@dataclass
class SETATTR(CODE):
    k: str
    v: INLINE
    t: str = ""

    def __str__(self):
        if self.t:
            return f"{self.k!s}: {self.t!s} = {self.v!s}"
        else:
            return f"{self.k!s} = {self.v!s}"


@dataclass
class LAMBDA(CODE):
    args: List[INLINE]
    expr: INLINE

    def __str__(self):
        return f"lambda {', '.join(map(str, self.args))}: {self.expr!s}"


class MODULE(CODE):
    def __init__(self, items: List[CODE]):
        self.items = items

    def __str__(self):
        content = ""
        prefix = ""
        last = None
        for item in self.items:
            if isinstance(last, FROM_IMPORT):
                if isinstance(item, FROM_IMPORT):
                    prefix = "\n"
                elif isinstance(item, SETATTR):
                    prefix = "\n\n"

            content += prefix
            if isinstance(item, DEF):
                prefix = "\n\n\n"
            else:
                prefix = "\n\n\n"
            last = item

            content += f"{item!s}"

        return content + "\n"

    def save(self, fp: str, allow_overwrite: bool = False):
        if not fp.endswith(".py"):
            fp += ".py"

        if os.path.exists(fp) and not allow_overwrite:
            raise FileExistsError(fp)

        with open(fp, mode="w", encoding="utf-8") as file:
            file.write(str(self))


class PACKAGE:
    def __init__(self, name: str, modules: Dict[str, MODULE]):
        assert name.isidentifier()
        assert '__init__' in modules
        assert all(module_name.isidentifier() for module_name in modules)
        self.name: str = name
        self.modules: Dict[str, MODULE] = modules

    def save(self, root: str, allow_overwrite: bool = False):
        path = os.path.join(root, self.name)

        if os.path.exists(path):
            if not allow_overwrite:
                raise FileExistsError(path)
        else:
            os.mkdir(path=path)

        for module_name, module in self.modules.items():
            module_path = os.path.join(path, module_name)
            module.save(fp=module_path, allow_overwrite=allow_overwrite)


class METHODS:
    @classmethod
    def INIT(cls, *args: ARG) -> DEF:
        body: LINES = LINES([SETATTR(k=f"self.{arg.k}", v=arg.k, t=arg.t) for arg in args])
        return DEF(name="__init__", args=ARGS(ARG("self"), *args), body=body)

    @classmethod
    def REPR(cls, *args: ARG) -> DEF:
        expr: str = "{self.__class__.__name__}(" + ", ".join("{self." + arg.k + "!r}" for arg in args) + ")"
        return DEF(name="__repr__", args=ARGS(ARG("self")), body=LINES([RETURN(FSTR(expr))]))
