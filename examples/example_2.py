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
    sep = "  "


class BlocP(OP1B):
    seps = ("( ", " )")


lexer, parser, builder, engine = base(
    # BLOCS
    [BlocP, match("LP") & match("L0").in_("*") & match("RP")],
    # OPERATORS
    [
        Pow,
        match("L3").in_("*") & match("HAT") & match("L2").in_("*"),
        match("L3").in_("*") & match("*.POWER").in_("*"),
    ],
    [
        Mul,
        match("L2").in_("*") & match("STAR") & match("L1").in_("*"),
        (match("Integer") | match("Decimal")).in_("*") & match("L1").in_("*")
    ],
    [Div, match("L2").in_("*") & match("SLASH") & match("L1").in_("*")],
    [Add, match("L1").in_("*") & match("PLUS") & match("L0").in_("*")],
    [Sub, match("L1").in_("*") & match("MINUS") & match("L0").in_("*")],
    # UNITS
    [Id, match("ID").in_("*")],
    [Integer, match("INTEGER").in_("*")],
    [Decimal, match("DECIMAL").in_("*")],

)

lexer.add_pattern("PLUS", mode="str", expr="+")
lexer.add_pattern("MINUS", mode="str", expr="-")
lexer.add_pattern("STAR", mode="str", expr="*")
lexer.add_pattern("SLASH", mode="str", expr="/")
lexer.add_pattern("HAT", mode="str", expr="^")

lexer.add_pattern("LP", mode="str", expr="(")
lexer.add_pattern("RP", mode="str", expr=")")

lexer.add_pattern("SQR.POWER", mode="str", expr="²", value=Integer(2))
lexer.add_pattern("CUBE.POWER", mode="str", expr="³", value=Integer(3))

lexer.add_pattern("ID", mode="re", expr=r"[a-zA-Z_][a-zA-Z0-9_]*")
lexer.add_pattern("DECIMAL", mode="re", expr=r"[0-9]+\.[0-9]*|\.[0-9]+", value=float)
lexer.add_pattern("INTEGER", mode="re", expr=r"[0-9]+", value=int)

parser.add_routine("L0", match("Add") | match("Sub") | match("L1"))
parser.add_routine("L1", match("Mul") | match("Div") | match("L2"))
parser.add_routine("L2", match("Pow") | match("L3"))
parser.add_routine("L3", match("Id") | match("Integer") | match("Decimal") | match("BlocP"))

if __name__ == "__main__":
    text = True
    while text:
        text = input("please enter a formula : ")
        if text:
            result = engine.read(text)
            if not result:
                print("The formula have not been parsed correctly")
            else:
                print(repr(result))
else:
    text = "3 * x ^ 2 + ( 1 - 6 ) + 4"

    result = engine.read(text)

    print(text)
    print()
    print(result)
    print(repr(result))
