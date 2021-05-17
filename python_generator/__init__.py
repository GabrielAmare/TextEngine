from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional, List, Union, Dict

__all__ = [
    "CODE",
    "RAW", "SCOPE",
    "IF",
    "RETURN", "YIELD", "RAISE",
    "SWITCH",
    "ARGS",
    "DEF", "CALL", "CLASS", "PIPE",
    "EXCEPTION",
    "STR", "FSTR", "LIST",
    "SETATTR",
    "CONDITION", "EQ", "NE", "IN", "NOT_IN", "LT", "LE", "GT", "GE", "ISINSTANCE",
    "MODULE", "PACKAGE",
    "LAMBDA",
    "METHODS",
    "PASS", "CONTINUE", "BREAK",
    "IMPORT_SECTION", "IMPORT_ALL",
    "FOR", "WHILE", "VAR"
]

PASS = "pass"
CONTINUE = "continue"
BREAK = "break"


def indent(text) -> str:
    if isinstance(text, str):
        return "\n".join("    " + line for line in text.split("\n"))
    else:
        return indent(str(text))


class CODE:
    def __str__(self):
        raise NotImplementedError

    def __and__(self, other) -> SCOPE:
        left = self.statements if isinstance(self, SCOPE) else [self]
        right = other.statements if isinstance(other, SCOPE) else [other]
        return SCOPE(*left, *right)


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
class SCOPE(CODE):
    statements: List[C]

    def __str__(self):
        r = ""
        prefix = ""
        for line in self.statements:
            r += prefix
            r += str(line)
            if isinstance(line, DEF):
                prefix = "\n\n"
            else:
                prefix = "\n"
        return r

        # return "\n".join(map(str, self.lines))

    def while_(self, cond) -> WHILE:
        return WHILE(cond=cond, body=self)


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
    elements: Optional[List[C]] = None

    def __str__(self):
        if self.elements is None:
            return "[]"
        else:
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


class _CALLABLE:
    def call(self, *args, **kwargs) -> CALL:
        return CALL(self, ARGS(*args, **kwargs))


class _NAME_CALLABLE(_CALLABLE):
    name: str

    def call(self, *args, **kwargs) -> CALL:
        return CALL(self.name, ARGS(*args, **kwargs))


class _PIPABLE:
    def pipe(self, *args) -> PIPE:
        return PIPE(self, *args)

    def getattr(self, obj) -> PIPE:
        return PIPE(self, obj)


class VAR(CODE, _NAME_CALLABLE, _PIPABLE):
    def __init__(self, name: str):
        assert name.isidentifier()
        self.name: str = name

    def __str__(self):
        return self.name

    def set(self, v: Union[CODE, str], t: str = "") -> SETATTR:
        return SETATTR(k=self.name, v=v, t=t)


@dataclass
class DEF(CODE, _NAME_CALLABLE):
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
    name: Union[str, _CALLABLE]
    args: Optional[ARGS] = None

    def __str__(self):
        if self.args is None:
            return f"{self.name!s}()"
        else:
            return f"{self.name!s}({self.args!s})"


class PIPE(CODE, _PIPABLE, _CALLABLE):
    def __init__(self, *items):
        self.items = items

    def __str__(self):
        return ".".join(map(str, self.items))


@dataclass
class SETATTR(CODE):
    k: Union[str, VAR]
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


@dataclass
class FOR(CODE):
    args: ARGS
    iterator: INLINE
    body: SCOPE

    def __str__(self):
        return f"for {self.args!s} in {self.iterator!s}:\n{indent(str(self.body))}"


@dataclass
class WHILE(CODE):
    cond: INLINE
    body: SCOPE

    def __str__(self):
        return f"while {self.cond!s}:\n{indent(str(self.body))}"


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
        body: SCOPE = SCOPE([SETATTR(k=f"self.{arg.k}", v=arg.k, t=arg.t) for arg in args])
        return DEF(name="__init__", args=ARGS(ARG("self"), *args), body=body)

    @classmethod
    def REPR(cls, *args: ARG) -> DEF:
        expr: str = "{self.__class__.__name__}(" + ", ".join("{self." + arg.k + "!r}" for arg in args) + ")"
        return DEF(name="__repr__", args=ARGS(ARG("self")), body=SCOPE([RETURN(FSTR(expr))]))


IMPORT_ALL = "*"


class IMPORT_SECTION(CODE):
    def __init__(self):
        self.imports: Dict[str, List[str]] = {}

    def __setitem__(self, module: str, name: str):
        self.imports[module] = [name]

    def append(self, module: str, name: str):
        self.imports.setdefault(module, [])
        if IMPORT_ALL not in self.imports[module]:
            if name == IMPORT_ALL:
                self.imports[module] = [name]
            elif name not in self.imports[module]:
                self.imports[module].append(name)

    def extend(self, module: str, *names: str):
        for name in names:
            self.append(module, name)

    def __str__(self):
        return str(SCOPE([
            FROM_IMPORT(module, ARGS(*names))
            for module, names in self.imports.items()
        ]))
