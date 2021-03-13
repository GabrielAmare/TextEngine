from text_engine import *


class Variable:
    def __init__(self, name):
        self.name = name


class Integer:
    def __init__(self, value):
        self.value = value


class Decimal:
    def __init__(self, value):
        self.value = value


class OP1:
    def __init__(self, one):
        self.one = one

    @classmethod
    def make(cls, name):
        exec(f"""class {name}(OP1):\n\tpass""")
        return eval(name)


class OP2:
    def __init__(self, one, two):
        self.one = one
        self.two = two

    @classmethod
    def make(cls, name):
        exec(f"""class {name}(OP2):\n\tpass""")
        return eval(name)


class Equations:
    def __init__(self, *equations):
        self.equations = equations


class Arguments:
    def __init__(self, *arguments):
        self.arguments = arguments


lexer, parser, builder, engine = base(
    [Equations, match("L-2 in *").sep_by("NEWLINE", backward=True)],
    [Arguments, match("L0 in *").sep_by("COMMA", backward=True).wrapped_by("LP", "RP")],

    [OP2.make("Eq"), match("L-2 in *") & match("EQUAL") & match("L-1 in *")],

    [OP2.make("Call"), match("Variable in *") & match("Arguments in *")],

    [OP2.make("Add"), match("L0 in *") & match("PLUS") & match("L2 in *")],
    [OP2.make("Sub"), match("L0 in *") & match("MINUS") & match("L2 in *")],

    [OP1.make("Neg"), match("MINUS") & match("L2 in *")],

    [OP2.make("Mul"), match("L2 in *") & match("STAR") & match("L3 in *"),
     match("Integer in *") & match("L3 in *")],
    [OP2.make("Div"), match("L2 in *") & match("SLASH") & match("L3 in *")],

    [OP2.make("Pow"), match("L3 in *") & match("HAT") & match("L4 in *"),
     match("L3 in *") & match("Integer in *")],
    [OP1.make("BlocP"), match("L0 in *").wrapped_by("LP", "RP")],
    [Variable, match("ID as name")],
    [Integer, match("INT as value"), match("*.POWER as value")],
    [Decimal, match("FLOAT as value")],
    pattern_libs=["maths", "units", "blocs"]
)

lexer.add_pattern("SQR.POWER", mode="str", expr="²", value=2)
lexer.add_pattern("CUBE.POWER", mode="str", expr="³", value=3)
lexer.add_pattern("NEWLINE.SYMBOL", mode="str", expr="\n")
lexer.add_pattern("COMMA.SYMBOL", mode="str", expr=",")

parser.add_routine("L4", match("BlocP") | match("Variable") | match("Integer") | match("Decimal"))
parser.add_routine("L3", match("Pow") | match("L4"))
parser.add_routine("L2", match("Mul") | match("Div") | match("L3"))
parser.add_routine("L1", match("Neg") | match("L2"))
parser.add_routine("L0", match("Add") | match("Sub") | match("L1"))
parser.add_routine("L-1", match("Call") | match("L0"))
parser.add_routine("L-2", match("Eq") | match("L-1"))

chart = {
    "*": dict(bg="black", fg="white", bd=2, relief="sunken", font=("Consolas", 12, "bold"), padx=5, pady=5),
    "ID": dict(fg="red"),
    "INT": dict(fg="blue"),
    "FLOAT": dict(fg="blue"),
    "*.SYMBOL": dict(fg="orange"),
    "*.POWER": dict(fg="purple"),
}

if __name__ == '__main__':
    # text = "y = x + 2\nz = x²+y²\nx = y/z"
    # text = "3*x² + 6 + 2"
    # text = "x^y^z"
    # text = "(1-3x²)/(1+6x²)"
    # text = "r = x^2+y^2"
    # text = "y = f(x)\nz = g(x, y)"
    # text = "0 = h(x², y², z²)"

    text = "f(x, y, z)"

    display(*engine.results(text, backward=True))

    # app = tkEngine(engine, text, chart, backward=True)
    #
    # app.mainloop()
