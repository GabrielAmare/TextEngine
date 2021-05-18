from __future__ import annotations
import os
from typing import Optional, List, Union, Dict, Tuple, Iterable
from tools37 import ReprTable

__all__ = []

PASS = "pass"
CONTINUE = "continue"
BREAK = "break"
NONE = "None"
TRUE = "True"
FALSE = "False"


def indent(text: str) -> str:
    if isinstance(text, str):
        return "\n".join(f"    {line!s}" for line in text.split("\n"))
    else:
        return indent(str(text))


class STATEMENT:
    def SCOPE(self) -> SCOPE:
        return SCOPE(self)

    def BLOCK(self) -> BLOCK:
        return BLOCK(self)


class DEF(STATEMENT):
    def __init__(self, name: VAR_I, args: ARGS_I = None, block: BLOCK_I = None, t: FUNC_TYPE_I = None):
        self.name: VAR_O = VAR.parse(name)
        self.args: ARGS_O = ARGS.parse(args)
        self.block: BLOCK_O = BLOCK.parse(block)
        self.t: FUNC_TYPE_O = FUNC_TYPE.parse(t)

    def __str__(self):
        return f"def {self.name!s}({self.args!s}){self.t!s}:{self.block!s}"


class CLASS(STATEMENT):
    def __init__(self, name: VAR_I, block: BLOCK_I = None, herits: CLASS_HERITS_I = None):
        self.name: VAR_O = VAR.parse(name)
        self.herits: CLASS_HERITS_O = CLASS_HERITS.parse(herits)
        self.block: BLOCK_O = BLOCK.parse(block)

    def __str__(self):
        return f"class {self.name!s}{self.herits!s}:{self.block!s}"

    def METHOD(self, name: str, args: ARGS, block: Union[BLOCK, STATEMENT] = None, rtype: TYPE = None) -> DEF:
        method = DEF(name, args, block, rtype)
        self.block.statements.append(method)
        return method


class FOR(STATEMENT):
    def __init__(self, args: ARGS_I, iterator: EXPRESSION, block: BLOCK_I = None, alt: Union[ELSE, ELIF] = None):
        self.args: ARGS_O = ARGS.parse(args)
        self.iterator: EXPRESSION = iterator
        self.block: BLOCK_O = BLOCK.parse(block)
        self.alt: Union[ELSE, ELIF] = alt or ELSE()

    def __str__(self):
        return f"for {self.args!s} in {self.iterator!s}:{self.block!s}{self.alt!s}"


class WHILE(STATEMENT):
    def __init__(self, condition: EXPRESSION, block: BLOCK_I = None, alt: Union[ELSE, ELIF] = None):
        self.condition: EXPRESSION = condition
        self.block: BLOCK_O = BLOCK.parse(block)
        self.alt: Union[ELSE, ELIF] = alt or ELSE()

    def __str__(self):
        return f"while {self.condition!s}:{self.block!s}{self.alt!s}"


class IF(STATEMENT):
    def __init__(self, condition: EXPRESSION, block: BLOCK_I = None, alt: ALT_I = None):
        self.condition: EXPRESSION = condition
        self.block: BLOCK_O = BLOCK.parse(block)
        self.alt: ALT_O = ALT.parse(alt)

    def __str__(self):
        return f"if {self.condition!s}:{self.block!s}{self.alt!s}"


class ASSIGN(STATEMENT):
    def __init__(self, o: OBJECT, v: EXPRESSION):
        self.o: OBJECT = o
        self.v: EXPRESSION = v

    def __str__(self):
        return f"{self.o!s} = {self.v!s}"


class SETATTR(STATEMENT):
    def __init__(self, o: OBJECT, k: VAR_I, v: EXPRESSION, t: TYPE_I = None):
        self.o: OBJECT = o
        self.k: VAR = VAR.parse(k)
        self.v: EXPRESSION = v
        self.t: TYPE_O = TYPE.parse(t)

        self.alias = ASSIGN(TYPED_OBJECT(GETATTR(o, k), t), v)

    def __str__(self):
        return f"{self.alias!s}"


class SETITEM(STATEMENT):
    def __init__(self, o: OBJECT, k, v, t: TYPE = None):
        self.o = o
        self.k = k
        self.v = v
        self.t = t

        self.alias = ASSIGN(TYPED_OBJECT(GETITEM(o, k), t), v)


__all__ += ["STATEMENT", "DEF", "CLASS", "FOR", "WHILE", "IF", "ASSIGN", "SETATTR", "SETITEM"]


class ALT:
    @classmethod
    def parse(cls, obj: ALT_I) -> ALT_O:
        if obj is None:
            return None
        elif isinstance(obj, cls):
            return obj
        elif isinstance(obj, IF):
            return ELIF(obj.condition, obj.block, obj.alt)
        else:
            return ELSE(*BLOCK.parse(obj).statements)


class ELIF(ALT):
    def __init__(self, condition: EXPRESSION, block: BLOCK_I = None, alt: ALT_I = None):
        self.condition: EXPRESSION = condition
        self.block: BLOCK = BLOCK.parse(block)
        self.alt: ALT_O = ALT.parse(alt)

    def __str__(self):
        return f"\nelif {self.condition!s}:{self.block!s}{self.alt!s}"


class ELSE(ALT):
    def __init__(self, *statements):
        self.block: BLOCK = BLOCK(*statements)

    def __str__(self):
        return f"\nelse:{self.block!s}" if self.block.statements else ""


__all__ += ["ELIF", "ELSE"]


class RAISE(STATEMENT):
    def __init__(self, expr: EXPRESSION):
        self.expr: EXPRESSION = expr

    def __str__(self):
        return f"raise {self.expr!s}"


class RETURN(STATEMENT):
    def __init__(self, expr: Union[EXPRESSION, ARGS]):
        self.expr: Union[EXPRESSION, ARGS] = expr

    def __str__(self):
        return f"return {self.expr!s}"


class YIELD(STATEMENT):
    def __init__(self, expr: Union[EXPRESSION, ARGS]):
        self.expr: Union[EXPRESSION, ARGS] = expr

    def __str__(self):
        return f"yield {self.expr!s}"


__all__ += ["END_FUNC_STATEMENT", "RETURN", "YIELD", "RAISE"]


class SCOPE:
    @classmethod
    def parse(cls, obj: SCOPE_I) -> SCOPE_O:
        if obj is None:
            return cls()
        elif isinstance(obj, cls):
            return obj
        elif isinstance(obj, STATEMENT):
            return cls(obj)
        elif hasattr(obj, '__iter__'):
            return cls(*obj)
        else:
            raise TypeError(type(obj))

    def __init__(self, *statements: STATEMENT):
        self.statements: List[STATEMENT] = []
        for statement in statements:
            assert isinstance(statement, STATEMENT), type(statement)
            self.statements.append(statement)

    def __str__(self):
        r = ""
        prefix = ""
        for statement in self.statements:
            r += prefix
            r += str(statement)
            if isinstance(statement, DEF):
                prefix = "\n\n"
            else:
                prefix = "\n"
        return r

        # return "\n".join(map(str, self.lines))

    def extract_imports(self) -> List[Union[IMPORT, IMPORT.FROM]]:
        """This method will extract import statements from the scope and it's subscopes"""
        keep = []
        throw = []
        for statement in self.statements:
            if isinstance(statement, (IMPORT, IMPORT.FROM)):
                throw.append(statement)
            else:
                keep.append(statement)

            if isinstance(statement, (IF, ELIF, ELSE, FOR, WHILE, CLASS, DEF)):
                throw.extend(statement.block.extract_imports())

            if isinstance(statement, (IF, ELIF, FOR, WHILE)):
                throw.extend(statement.alt.block.extract_imports())

        self.statements = keep
        return throw


class BLOCK(SCOPE):
    @classmethod
    def parse(cls, obj: BLOCK_I) -> BLOCK_O:
        if obj is None:
            return cls()
        elif type(obj) is SCOPE:
            return cls(*obj.statements)
        elif isinstance(obj, cls):
            return obj
        elif hasattr(obj, '__iter__'):
            return cls(*obj)
        elif isinstance(obj, STATEMENT):
            return cls(obj)
        else:
            raise TypeError(type(obj))

    def __str__(self):
        return "\n" + indent(super().__str__() if self.statements else "pass")

    def WHILE(self, condition: CONDITION, alt: ELSE = None) -> WHILE:
        return WHILE(condition, self, alt)

    def IF(self, condition: CONDITION, alt: Union[ELSE, ELIF] = None) -> IF:
        return IF(condition, self, alt)


__all__ += ["SCOPE", "BLOCK"]


class EXPRESSION:
    @classmethod
    def parse(cls, obj: EXPRESSION_I) -> EXPRESSION_O:
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, str):
            return STR(obj)
        elif isinstance(obj, int):
            return INT(obj)
        else:
            raise TypeError(type(obj))

    def RETURN(self):
        return RETURN(self)

    def YIELD(self):
        return YIELD(self)

    def RAISE(self):
        return RAISE(self)

    def EQ(self, other: EXPRESSION_I) -> EQ:
        return EQ(self, other)

    def NE(self, other: EXPRESSION_I) -> NE:
        return NE(self, other)

    def LT(self, other: EXPRESSION_I) -> LT:
        return LT(self, other)

    def LE(self, other: EXPRESSION_I) -> LE:
        return LE(self, other)

    def GT(self, other: EXPRESSION_I) -> GT:
        return GT(self, other)

    def GE(self, other: EXPRESSION_I) -> GE:
        return GE(self, other)

    def IN(self, other: EXPRESSION_I) -> IN:
        return IN(self, other)

    def NOT_IN(self, other: EXPRESSION_I) -> NOT_IN:
        return NOT_IN(self, other)

    def IS(self, other: EXPRESSION_I) -> IS:
        return IS(self, other)

    def IS_NOT(self, other: EXPRESSION_I) -> IS_NOT:
        return IS_NOT(self, other)

    def AND(self, other: EXPRESSION_I) -> AND:
        return AND(self, other)

    def OR(self, other: EXPRESSION_I) -> OR:
        return OR(self, other)


class CONDITION(EXPRESSION):
    def IF(self, block: BLOCK = None, alt: Union[ELSE, ELIF] = None) -> IF:
        return IF(self, block, alt)

    def ELIF(self, block: BLOCK = None, alt: Union[ELSE, ELIF] = None) -> ELIF:
        return ELIF(self, block, alt)

    def WHILE(self, block: BLOCK = None, alt: Union[ELSE, ELIF] = None) -> WHILE:
        return WHILE(self, block, alt)


class AND(CONDITION):
    def __init__(self, *terms: EXPRESSION_I):
        self.terms: List[EXPRESSION_O] = list(map(EXPRESSION.parse, terms))

    def __str__(self):
        return " and ".join(map(str, self.terms))


class OR(CONDITION):
    def __init__(self, *terms: EXPRESSION_I):
        self.terms: List[EXPRESSION_O] = list(map(EXPRESSION.parse, terms))

    def __str__(self):
        return " or ".join(map(str, self.terms))


class LAMBDA(EXPRESSION):
    def __init__(self, args: ARGS_I = None, expr: EXPRESSION = None):
        self.args: ARGS_O = ARGS.parse(args)
        self.expr: EXPRESSION = expr or NONE

    def __str__(self):
        return f"lambda {self.args!s}: {self.expr!s}"


__all__ += ["EXPRESSION", "CONDITION", "AND", "OR"]


class OBJECT(EXPRESSION):
    def SETATTR(self, k, v, t: TYPE_I = None) -> SETATTR:
        return SETATTR(self, k, v, t)

    def GETATTR(self, k) -> GETATTR:
        return GETATTR(self, k)

    def SETITEM(self, k, v, t: TYPE_I = None) -> SETITEM:
        return SETITEM(self, k, v, t)

    def GETITEM(self, k) -> GETITEM:
        return GETITEM(self, k)

    def CALL(self, *args, **kwargs) -> CALL:
        return CALL(self, ARGS(*args, **kwargs))

    def ASSIGN(self, v, t: TYPE_I = None) -> ASSIGN:
        return ASSIGN(TYPED_OBJECT(self, t), v)

    @property
    def AS_ARG(self) -> AS_ARG:
        return AS_ARG(self)

    @property
    def AS_KWARG(self) -> AS_KWARG:
        return AS_KWARG(self)

    @property
    def TYPE_OF(self) -> CALL:
        return VAR("type").CALL(self)


class TYPED_OBJECT(OBJECT):
    def __init__(self, o: OBJECT, t: TYPE_I = None):
        self.o: OBJECT = o
        self.t: TYPE_O = TYPE.parse(t)

    def __str__(self):
        return f"{self.o!s}" if self.t is None else f"{self.o!s}: {self.t!s}"


class GETATTR(OBJECT):
    def __init__(self, obj: OBJECT, key: VAR_I):
        self.obj: OBJECT = obj
        self.key: VAR_O = VAR.parse(key)

    def __str__(self):
        return f"{self.obj!s}.{self.key!s}"


class GETITEM(OBJECT):
    def __init__(self, obj: OBJECT, key: EXPRESSION):
        self.obj: OBJECT = obj
        self.key: EXPRESSION = key

    def __str__(self):
        return f"{self.obj!s}[{self.key!s}]"


class CALL(OBJECT):
    def __init__(self, obj: OBJECT, args: ARGS = None):
        self.obj: OBJECT = obj
        self.args: ARGS = args or ARGS()

    def __str__(self):
        return f"{self.obj!s}({self.args!s})"


class VAR(OBJECT):
    @classmethod
    def parse(cls, obj: VAR_I) -> VAR_O:
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, str):
            return cls(obj)
        # elif isinstance(obj, ARG):
        #     return obj.k
        else:
            raise TypeError(type(obj))

    def __init__(self, name: str):
        # assert all(sname.isidentifier() for sname in name.split('.')), repr(name)
        self.name: str = name

    def __hash__(self):
        return hash((type(self), self.name))

    def __eq__(self, other: Union[VAR, str]) -> bool:
        if isinstance(other, VAR):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        else:
            raise NotImplementedError

    def __lt__(self, other):
        if isinstance(other, VAR):
            return self.name < other.name
        elif isinstance(other, str):
            return self.name < other
        else:
            raise NotImplementedError

    def __str__(self):
        return self.name

    def ARG(self, v: Optional[EXPRESSION_I] = None, t: TYPE_I = None) -> ARG:
        return ARG(self, v, t)


class INT(OBJECT):
    def __init__(self, value: int):
        self.value: int = value

    def __str__(self):
        return f"{self.value!r}"


class STR(OBJECT):
    def __init__(self, content: str):
        self.content: str = content

    def __str__(self):
        return f"{self.content!r}"


class FSTR(OBJECT):
    def __init__(self, content: str):
        self.content: str = content

    def __str__(self):
        return f"f{self.content!r}"


class LIST(OBJECT):
    def __init__(self, content: list):
        self.content: list = content

    def __str__(self):
        if self.content:
            return f"[{', '.join(map(str, self.content))}]"
        else:
            return '[]'


class DICT(OBJECT):
    def __init__(self, content: dict):
        self.content: dict = content

    def __str__(self):
        if self.content:
            if all(isinstance(k, str) and k.isidentifier() for k in self.content.keys()):
                return f"dict({', '.join(f'{k!s}={v!r}' for k, v in self.content.items())})"
            else:
                return f"{{{', '.join(f'{k!r}: {v!r}' for k, v in self.content.items())}}}"
        else:
            return '{}'


class TUPLE(OBJECT):
    def __init__(self, content: tuple):
        self.content: tuple = content

    def __str__(self):
        if len(self.content) == 0:
            return '()'
        elif len(self.content) == 1:
            return f"({self.content[0]!s}, )"
        else:
            return f"({', '.join(map(str, self.content))})"


__all__ += ["OBJECT", "TYPED_OBJECT", "GETATTR", "GETITEM", "CALL", "VAR", "INT", "STR", "FSTR", "LIST", "DICT",
            "TUPLE"]

SELF = VAR("self")
CLS = VAR("cls")

__all__ += ["SELF", "CLS"]


class AS_KWARG:
    def __init__(self, obj: OBJECT):
        self.obj: OBJECT = obj

    def __str__(self):
        return f"**{self.obj!s}"


class AS_ARG:
    def __init__(self, obj: OBJECT):
        self.obj: OBJECT = obj

    def __str__(self):
        return f"*{self.obj!s}"


__all__ += ["AS_KWARG", "AS_ARG"]


class COMPARISON(CONDITION):
    symbol: str

    def __init__(self, left: EXPRESSION, right: EXPRESSION):
        self.left = left
        self.right = right

    def __str__(self):
        return f"{self.left!s} {self.__class__.symbol} {self.right!s}"


class EQ(COMPARISON):
    symbol = '=='


class NE(COMPARISON):
    symbol = '!='


class LT(COMPARISON):
    symbol = '<'


class LE(COMPARISON):
    symbol = '<='


class GT(COMPARISON):
    symbol = '>'


class GE(COMPARISON):
    symbol = '>='


class IN(COMPARISON):
    symbol = 'in'


class NOT_IN(COMPARISON):
    symbol = 'not in'


class IS(COMPARISON):
    symbol = 'is'


class IS_NOT(COMPARISON):
    symbol = 'is not'


__all__ += ["COMPARISON", "EQ", "NE", "LT", "LE", "GT", "GE", "IN", "NOT_IN", "IS", "IS_NOT"]


class ARGS:
    @classmethod
    def parse(cls, obj: ARGS_I) -> ARGS_O:
        if obj is None:
            return None
        elif isinstance(obj, ARGS):
            return obj
        elif isinstance(obj, ARG):
            return ARGS(obj)
        elif hasattr(obj, "__iter__"):
            return ARGS(*obj)
        else:
            return cls(VAR.parse(obj))

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return ", ".join(list(map(str, self.args)) + [f"{key}={val}" for key, val in self.kwargs.items()])

    def RETURN(self) -> RETURN:
        return RETURN(self)

    def YIELD(self) -> YIELD:
        return YIELD(self)


class ARG:
    def __init__(self, k: VAR_I, v: Optional[EXPRESSION_I] = None, t: TYPE_I = None):
        self.k: VAR = VAR.parse(k)
        self.v: EXPRESSION = None if v is None else EXPRESSION.parse(v)
        self.t: TYPE_O = TYPE.parse(t)

        self.to: TYPED_OBJECT = TYPED_OBJECT(self.k, self.t)

    def __eq__(self, other):
        return type(self) is type(other) and self.k == other.k and self.v == other.v and self.t == other.t

    def __lt__(self, other):
        if type(self) is type(other):
            return (self.k, self.v, self.t) < (other.k, other.v, other.t)
        else:
            raise NotImplementedError

    def __str__(self):
        return f"{self.to}" if self.v is None else f"{self.to}={self.v}"


class IMPORT(STATEMENT):
    def __init__(self, name: VAR_I):
        self.name: VAR_O = VAR.parse(name)

    def __str__(self):
        return f"import {self.name!s}"

    class ALL(STATEMENT):
        def __init__(self, name: VAR_I):
            self.name: VAR_O = VAR.parse(name)

        def __str__(self):
            return f"from {self.name!s} import *"

    class FROM(STATEMENT):
        def __init__(self, name: VAR_I, args: IMPORT_FROM_ARGS_I = None):
            self.name: VAR_O = VAR.parse(name)
            self.args: IMPORT_FROM_ARGS_O = IMPORT.FROM.ARGS.parse(args)

        def __str__(self):
            return f"from {self.name!s} import {self.args!s}"

        class ARG:
            @classmethod
            def parse(cls, obj: IMPORT_FROM_ARG_I) -> IMPORT_FROM_ARG_O:
                if isinstance(obj, cls):
                    return obj
                elif isinstance(obj, tuple):
                    return cls(*obj)
                else:
                    return cls(obj)

            def __init__(self, name: VAR_I, as_: Optional[VAR_I] = None):
                self.name: VAR_O = VAR.parse(name)
                self.as_: Optional[VAR_O] = None if as_ is None else VAR.parse(as_)

            def __hash__(self):
                return hash((type(self), self.name, self.as_))

            def __eq__(self, other):
                return type(self) is type(other) and self.name == other.name and self.as_ == other.as_

            def __lt__(self, other):
                if type(self) is type(other):
                    return (self.name, self.as_) < (other.name, other.as_)
                else:
                    raise NotImplementedError

            def __str__(self):
                return f"{self.name!s}" if self.as_ is None else f"{self.name!s} as {self.as_}"

        class ARGS:
            @classmethod
            def parse(cls, obj: IMPORT_FROM_ARGS_I) -> IMPORT_FROM_ARGS_O:
                if isinstance(obj, cls):
                    return obj
                elif isinstance(obj, list):
                    return cls(*obj)
                else:
                    return cls(obj)

            def __init__(self, *args: IMPORT_FROM_ARG_I):
                self.args: List[IMPORT_FROM_ARG_O] = list(map(IMPORT.FROM.ARG.parse, args))

            def __iter__(self):
                return iter(self.args)

            def __str__(self):
                return ", ".join(map(str, self.args))


class MODULE:
    def __init__(self, name: VAR_I, scope: SCOPE_I):
        self.name: VAR_O = VAR.parse(name)
        self.scope: SCOPE_O = SCOPE.parse(scope)

    def simplify_imports(self):
        """
            This method will search in the whole module for IMPORT|IMPORT.FROM statements and put them at the start of the module
        """
        import_statements = self.scope.extract_imports()

        imports: List[VAR_O] = []
        imports_all: List[VAR_O] = []
        imports_from: Dict[VAR_O, List[IMPORT_FROM_ARG_O]] = {}

        for statement in import_statements:
            if isinstance(statement, IMPORT):
                imports.append(statement.name)
            elif isinstance(statement, IMPORT.ALL):
                imports_all.append(statement.name)
            elif isinstance(statement, IMPORT.FROM):
                if statement.name in imports_from:
                    imports_from[statement.name].extend(statement.args)
                else:
                    imports_from[statement.name] = list(statement.args)
            else:
                raise TypeError(type(statement))

        import_statements = [
            *(IMPORT(name) for name in sorted(imports)),
            *(IMPORT.ALL(name) for name in sorted(imports_all)),
            *(IMPORT.FROM(name, sorted(set(args))) for name, args in sorted(imports_from.items()) if
              name not in imports_all)
        ]

        self.scope.statements = [*import_statements, *self.scope.statements]

    def __str__(self):
        content = ""
        prefix = ""
        last = None
        for item in self.scope.statements:
            if isinstance(last, IMPORT.FROM):
                if isinstance(item, IMPORT.FROM):
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

    def save(self, root: str, allow_overwrite: bool = False):
        fp = os.path.join(root, f"{self.name!s}.py")

        if os.path.exists(fp) and not allow_overwrite:
            raise FileExistsError(fp)

        self.simplify_imports()

        with open(fp, mode="w", encoding="utf-8") as file:
            file.write(str(self))


class PACKAGE:
    def __init__(self, name: VAR_I, *modules: MODULE):
        assert '__init__' in [str(module.name) for module in modules], \
            "you must define a '__init__.py' module into a package !\n" + \
            "\n".join(f"{module.name}.py" for module in modules)
        self.name: VAR_O = VAR.parse(name)
        self.modules: List[MODULE] = list(modules)

    def __str__(self):
        rt = ReprTable.from_items(
            items=self.modules,
            config={
                "module name": lambda module: f"{module.name}.py",
                "module content": lambda module: str(module)
            }
        )

        return f"package : '{self.name}/'\n{rt!s}"

    def save(self, root: str, allow_overwrite: bool = False):
        path = os.path.join(root, str(self.name))

        if os.path.exists(path):
            if not allow_overwrite:
                raise FileExistsError(path)
        else:
            os.mkdir(path=path)

        for module in self.modules:
            module.save(root=path, allow_overwrite=allow_overwrite)


class METHODS:
    @classmethod
    def INIT(cls, *args: ARG) -> DEF:
        return DEF(
            "__init__",
            ARGS(VAR("self"), *args),
            [
                SELF.SETATTR(arg.k, arg.k, arg.t)
                for arg in args
            ]
        )

    @classmethod
    def REPR(cls, *args: ARG) -> DEF:
        return DEF(
            "__repr__",
            SELF,
            FSTR("{self.__class__.__name__}(" + ", ".join("{self." + str(arg.k) + "!r}" for arg in args) + ")").RETURN()
        )


########################################################################################################################
# SHORTCUT FUNCTIONS
########################################################################################################################

def ISINSTANCE(o, t) -> CALL:
    return VAR("isinstance").CALL(o, t)


def ISSUBCLASS(o, t) -> CALL:
    return VAR("issubclass").CALL(o, t)


def EXCEPTION(e) -> CALL:
    return VAR("Exception").CALL(e)


########################################################################################################################
# SHORTCUT STRUCTURES
########################################################################################################################


def SWITCH(cases: List[Tuple[EXPRESSION, BLOCK_I]], default: BLOCK_I = None) -> IF:
    if not cases:
        return BLOCK()

    current = default
    for condition, block in reversed(cases[1:]):
        current = ELIF(condition=condition, block=block, alt=current)
    condition, block = cases[0]
    return IF(condition=condition, block=block, alt=current)


########################################################################################################################
# INTERNAL BEHAVIORS
########################################################################################################################

class TYPE:
    @classmethod
    def parse(cls, obj: TYPE_I) -> TYPE_O:
        if obj is None:
            return None
        elif isinstance(obj, cls):
            return obj
        elif isinstance(obj, type):
            return cls(obj.__name__, obj.__module__)
        elif isinstance(obj, CLASS):
            return cls(obj.name)
        elif isinstance(obj, str):
            return cls(obj)

    def __init__(self, name: VAR_I, module: str = None):
        self.name: VAR_O = VAR.parse(name)
        self.module: Optional[str] = module

    def __str__(self):
        return f"{self.name!s}"


class FUNC_TYPE:
    @classmethod
    def parse(cls, obj: FUNC_TYPE_I) -> FUNC_TYPE_O:
        if isinstance(obj, cls):
            return obj
        else:
            return cls(TYPE.parse(obj))

    def __init__(self, t: TYPE_I):
        self.t: TYPE_O = TYPE.parse(t)

    def __str__(self):
        return "" if self.t is None else f" -> {self.t!s}"


class CLASS_HERITS:
    @classmethod
    def parse(cls, obj: CLASS_HERITS_I) -> CLASS_HERITS_O:
        if obj is None:
            return cls()
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, ARGS):
            pass
        else:
            raise TypeError(type(obj))

    def __init__(self, args: ARGS_I = None):
        self.args: ARGS_O = ARGS.parse(args)

    def __str__(self):
        return "" if self.args is None else f"({self.args!s})"


########################################################################################################################
# PARSING TYPES
########################################################################################################################

SCOPE_I = Optional[Union[SCOPE, STATEMENT, Iterable[STATEMENT]]]
SCOPE_O = SCOPE

BLOCK_I = Optional[Union[BLOCK, SCOPE, STATEMENT, Iterable[STATEMENT]]]
BLOCK_O = BLOCK

VAR_I = Union[str, VAR]
VAR_O = VAR

ARGS_I = Optional[Union[ARGS, ARG, Iterable[Union[ARG, VAR_I]], VAR_I]]
ARGS_O = Optional[ARGS]

TYPE_I = Optional[Union[TYPE, type, CLASS, VAR_I]]
TYPE_O = Optional[TYPE]

FUNC_TYPE_I = Union[FUNC_TYPE, TYPE_I]
FUNC_TYPE_O = FUNC_TYPE

CLASS_HERITS_I = Optional[Union[CLASS_HERITS, ARGS_I]]
CLASS_HERITS_O = CLASS_HERITS

IMPORT_FROM_ARG_I = Union[IMPORT.FROM.ARG, Tuple[VAR_I, VAR_I], Optional[VAR_I]]
IMPORT_FROM_ARG_O = IMPORT.FROM.ARG

IMPORT_FROM_ARGS_I = Union[IMPORT.FROM.ARGS, List[IMPORT_FROM_ARG_I], IMPORT_FROM_ARG_I]
IMPORT_FROM_ARGS_O = IMPORT.FROM.ARGS

EXPRESSION_I = Union[EXPRESSION, str, int]
EXPRESSION_O = EXPRESSION

ALT_I = Optional[Union[ALT, IF, BLOCK]]
ALT_O = Optional[ALT]
