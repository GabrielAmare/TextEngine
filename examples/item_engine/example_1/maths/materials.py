from item_engine.textbase import *
from itertools import starmap
from operator import eq


class Var:
    def __init__(self, name: str):
        self.name: str = name
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r})'
    
    def __str__(self):
        return str(self.name)
    
    def __eq__(self, other):
        return type(self) is type(other) and self.name == other.name


class Int:
    def __init__(self, value: int):
        self.value: int = value
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.value!r})'
    
    def __str__(self):
        return str(self.value)
    
    def __eq__(self, other):
        return type(self) is type(other) and self.value == other.value


class Float:
    def __init__(self, value: float):
        self.value: float = value
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.value!r})'
    
    def __str__(self):
        return str(self.value)
    
    def __eq__(self, other):
        return type(self) is type(other) and self.value == other.value


class IntPow:
    def __init__(self, value: int):
        self.value: int = value
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.value!r})'
    
    def __str__(self):
        return str(self.value)
    
    def __eq__(self, other):
        return type(self) is type(other) and self.value == other.value


class ForAll:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'∀{self.c0!s} ∈ {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Exists:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'∃{self.c0!s} ∈ {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Constraint:
    def __init__(self, c0, c1, c2):
        self.c0 = c0
        self.c1 = c1
        self.c2 = c2
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r}, {self.c2!r})'
    
    def __str__(self):
        return f'{self.c0!s}, {self.c1!s} | {self.c2!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1 and self.c2 == other.c2


class EnumV:
    def __init__(self, *cs):
        self.cs = cs
    
    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(map(repr, self.cs))})"
    
    def __str__(self):
        return ', '.join(map(str, self.cs))
    
    def __eq__(self, other):
        return type(self) is type(other) and all(starmap(eq, zip(self.cs, other.cs)))


class Set:
    def __init__(self, c0):
        self.c0 = c0
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r})'
    
    def __str__(self):
        return f'{{ {self.c0!s} }}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0


class Pow:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} ^ {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Neg:
    def __init__(self, c0):
        self.c0 = c0
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r})'
    
    def __str__(self):
        return f' - {self.c0!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0


class Mul:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} * {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Div:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} / {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Add:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} + {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Sub:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} - {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Eq:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} == {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Lt:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} < {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Le:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} <= {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Gt:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} > {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Ge:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} >= {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Not:
    def __init__(self, c0):
        self.c0 = c0
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r})'
    
    def __str__(self):
        return f'not {self.c0!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0


class And:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} and {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Or:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s} or {self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Attr:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return f'{self.c0!s}={self.c1!s}'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0 and self.c1 == other.c1


class Par:
    def __init__(self, c0):
        self.c0 = c0
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.c0!r})'
    
    def __str__(self):
        return f'( {self.c0!s} )'
    
    def __eq__(self, other):
        return type(self) is type(other) and self.c0 == other.c0


class Equations:
    def __init__(self, *cs):
        self.cs = cs
    
    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(map(repr, self.cs))})"
    
    def __str__(self):
        return '\n'.join(map(str, self.cs))
    
    def __eq__(self, other):
        return type(self) is type(other) and all(starmap(eq, zip(self.cs, other.cs)))


def build(e: Element):
    if isinstance(e, Lemma):
        if e.value == '__FORALL__':
            return ForAll(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__EXISTS__':
            return Exists(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__CONSTRAINT__':
            return Constraint(build(e.data['c0']), build(e.data['c1']), build(e.data['c2']))
        elif e.value == '__ENUMV__':
            return EnumV(*map(build, e.data['cs']))
        elif e.value == '__SET__':
            return Set(build(e.data['c0']))
        elif e.value == '__POW__':
            return Pow(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__NEG__':
            return Neg(build(e.data['c0']))
        elif e.value == '__MUL__':
            return Mul(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__DIV__':
            return Div(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__ADD__':
            return Add(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__SUB__':
            return Sub(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__EQ__':
            return Eq(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__LT__':
            return Lt(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__LE__':
            return Le(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__GT__':
            return Gt(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__GE__':
            return Ge(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__NOT__':
            return Not(build(e.data['c0']))
        elif e.value == '__AND__':
            return And(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__OR__':
            return Or(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__ATTR__':
            return Attr(build(e.data['c0']), build(e.data['c1']))
        elif e.value == '__PAR__':
            return Par(build(e.data['c0']))
        elif e.value == '__EQUATIONS__':
            return Equations(*map(build, e.data['cs']))
        else:
            raise Exception(e.value)
    elif isinstance(e, Token):
        if e.value == 'VAR':
            return Var(str(e.content))
        elif e.value == 'INT':
            return Int(int(e.content))
        elif e.value == 'FLOAT':
            return Float(float(e.content))
        elif e.value == 'INT_POW':
            parse = lambda content: content.translate({8304: 48, 185: 49, 178: 50, 179: 51, 8308: 52, 8309: 53, 8310: 54, 8311: 55, 8312: 56, 8313: 57})
            return IntPow(int(parse(e.content)))
        else:
            raise Exception(e.value)
    else:
        raise Exception(e.value)
