from item_engine.textbase import *


class Var:
    def __init__(self, name: str):
        self.name: str = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.name!r})'
    
    def __str__(self):
        return str(self.name)


class Int:
    def __init__(self, value: int):
        self.value: int = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.value!r})'
    
    def __str__(self):
        return str(self.value)


class IntPow:
    def __init__(self, value: int):
        self.value: int = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.value!r})'
    
    def __str__(self):
        return str(self.value)


class ForAll:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'∀{self.c0!s} ∈ {self.c1!s}'


class Exists:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'∃{self.c0!s} ∈ {self.c1!s}'


class Constraint:
    def __init__(self, c0, c1, c2):
        self.c0 = None
        self.c1 = None
        self.c2 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r}, {self.c2!r})'
    
    def __str__(self):
        return r'{self.c0!s}, {self.c1!s} | {self.c2!s}'


class EnumV:
    def __init__(self, *cs):
        self.cs = cs
    
    def __repr__(self):
        return r"{self.__class__.__name__}({', '.join(map(repr, self.cs))})"
    
    def __str__(self):
        return ', '.join(map(str, self.cs))


class Set:
    def __init__(self, c0):
        self.c0 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r})'
    
    def __str__(self):
        return r'{{ {self.c0!s} }}'


class Pow:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s} ^ {self.c1!s}'


class Neg:
    def __init__(self, c0):
        self.c0 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r})'
    
    def __str__(self):
        return r' - {self.c0!s}'


class Mul:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s} * {self.c1!s}'


class Div:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s} / {self.c1!s}'


class Add:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s} + {self.c1!s}'


class Sub:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s} - {self.c1!s}'


class Eq:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s} == {self.c1!s}'


class Lt:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s} < {self.c1!s}'


class Le:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s} <= {self.c1!s}'


class Gt:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s} > {self.c1!s}'


class Ge:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s} >= {self.c1!s}'


class Not:
    def __init__(self, c0):
        self.c0 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r})'
    
    def __str__(self):
        return r'not {self.c0!s}'


class And:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s} and {self.c1!s}'


class Or:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s} or {self.c1!s}'


class Attr:
    def __init__(self, c0, c1):
        self.c0 = None
        self.c1 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r}, {self.c1!r})'
    
    def __str__(self):
        return r'{self.c0!s}={self.c1!s}'


class Par:
    def __init__(self, c0):
        self.c0 = None
    
    def __repr__(self):
        return r'{self.__class__.__name__}({self.c0!r})'
    
    def __str__(self):
        return r'( {self.c0!s} )'


class Equations:
    def __init__(self, *cs):
        self.cs = cs
    
    def __repr__(self):
        return r"{self.__class__.__name__}({', '.join(map(repr, self.cs))})"
    
    def __str__(self):
        return '\n'.join(map(str, self.cs))


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
        elif e.value == 'INT_POW':
            parse = lambda content: content.translate({8304: 48, 185: 49, 178: 50, 179: 51, 8308: 52, 8309: 53, 8310: 54, 8311: 55, 8312: 56, 8313: 57})
            return IntPow(int(parse(e.content)))
        else:
            raise Exception(e.value)
    else:
        raise Exception(e.value)
