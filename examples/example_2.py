from text_engine import *


class Id:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.name)})"

    def __str__(self):
        return self.name


class Integer:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __str__(self):
        return str(self.value)


class Decimal:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __str__(self):
        return str(self.value)


class Equations:
    def __init__(self, *equations):
        self.equations = equations

    def __repr__(self):
        return f"{self.__class__.__name__}(" + ",\n".join(map(repr, self.equations)) + ")"

    def __str__(self):
        return "\n".join(map(str, self.equations))


class OP1B:
    seps: (str, str)

    def __init__(self, inside):
        self.inside = inside

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.inside)})"

    def __str__(self):
        return self.seps[0] + str(self.inside) + self.seps[1]


class OP2N:
    sep: str

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.left)}, {repr(self.right)})"

    def __str__(self):
        return f"{str(self.left)}{self.sep}{str(self.right)}"


class Add(OP2N):
    sep = " + "


class Sub(OP2N):
    sep = " - "


class Mul(OP2N):
    sep = " * "


class Div(OP2N):
    sep = " / "


class Pow(OP2N):
    sep = " ^ "


class Attr(OP2N):
    sep = " = "


class BlocP(OP1B):
    seps = ("( ", " )")


class Call:
    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.name)}, " + ", ".join(map(repr, self.args)) + ")"

    def __str__(self):
        return f"{str(self.name)}(" + ", ".join(map(str, self.args)) + ")"


lexer, parser, builder, engine = base(
    # BLOCS
    [BlocP, match("LP") & match("L0").in_("*") & match("RP")],
    [Attr, match("Id").in_("*") & match("EQUAL") & match("L0").in_("*")],
    [Call, match("Id").in_("*") & match("LP") & match("L0").in_("*").sep_by("COMA", backward=True) & match("RP")],
    # OPERATORS
    [
        Pow,
        match("L2").in_("*") & match("HAT") & match("L3").in_("*"),
        match("L2").in_("*") & match("*.POWER").in_("*"),
    ],
    [
        Mul,
        match("L1").in_("*") & match("STAR") & match("L2").in_("*"),
        (match("Integer") | match("Decimal")).in_("*") & match("L2").in_("*")
    ],
    [Div, match("L1").in_("*") & match("SLASH") & match("L2").in_("*")],
    [Add, match("L0").in_("*") & match("PLUS") & match("L1").in_("*")],
    [Sub, match("L0").in_("*") & match("MINUS") & match("L1").in_("*")],
    # UNITS
    [Id, match("ID").in_("*")],
    [Integer, match("INTEGER").in_("*")],
    [Decimal, match("DECIMAL").in_("*")],
    [Equations, match("LB").in_("*").sep_by("NEWLINE", backward=True)]

)

lexer.add_pattern("PLUS", mode="str", expr="+")
lexer.add_pattern("MINUS", mode="str", expr="-")
lexer.add_pattern("STAR", mode="str", expr="*")
lexer.add_pattern("SLASH", mode="str", expr="/")
lexer.add_pattern("HAT", mode="str", expr="^")
lexer.add_pattern("EQUAL", mode="str", expr="=")
lexer.add_pattern("NEWLINE", mode="str", expr="\n")
lexer.add_pattern("COMA", mode="str", expr=",")

lexer.add_pattern("LP", mode="str", expr="(")
lexer.add_pattern("RP", mode="str", expr=")")

lexer.add_pattern("SQR.POWER", mode="str", expr="²", value=Integer(2))
lexer.add_pattern("CUBE.POWER", mode="str", expr="³", value=Integer(3))

lexer.add_pattern("ID", mode="re", expr=r"[a-zA-Z_][a-zA-Z0-9_]*")
lexer.add_pattern("DECIMAL", mode="re", expr=r"[0-9]+\.[0-9]*|\.[0-9]+", value=float)
lexer.add_pattern("INTEGER", mode="re", expr=r"[0-9]+", value=int)

parser.add_routine("LB", match("Attr") | match("L0"))
parser.add_routine("L0", match("Add") | match("Sub") | match("L1"))
parser.add_routine("L1", match("Mul") | match("Div") | match("L2"))
parser.add_routine("L2", match("Pow") | match("L3"))
parser.add_routine("L3", match("Call") | match("Id") | match("Integer") | match("Decimal") | match("BlocP"))

if __name__ == "__main__":
    text = """y = 3 * x ^ 2 + 1 - 6 + 4
t = x² + y² + z²
u = 2x - 3y + 7z
v = 10x-6.7z + 1.001y
f(x, x, x) * f(y, y, y) ^ f(z, z, z)"""

    result = engine.read(text, backward=True)

    print(text)
    print()
    print(result)
    print(repr(result))

    text = True
    while text:
        text = input("please enter a formula : ")
        if text:
            result = engine.read(text, backward=True)
            if not result:
                print("The formula have not been parsed correctly")
            else:
                print(repr(result))
