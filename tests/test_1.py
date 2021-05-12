from text_engine import *
import time


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


LP = ("(", "LP")
RP = (")", "RP")
COMMA = (", ", "COMMA")
EQUAL = (" = ", "EQUAL")

lexer, parser, builder, engine = base(
    # OPERATORS
    OP1B.builder("BlocP", LP, "L0", RP),
    OP2N.builder("Attr", "Id", EQUAL, "L0"),
    OP2R.builder("Call", "Id", LP, "Args", RP),
    [
        OP2N.cls("Pow", " ^ "),
        match("L2").in_("*") & match("HAT") & match("L3").in_("*"),
        match("L2").in_("*") & match("Integer").in_("*"),
    ],
    [
        OP2N.cls("Mul", " * "),
        match("L1").in_("*") & match("STAR") & match("L2").in_("*"),
        (match("Integer") | match("Decimal")).in_("*") & match("L2").in_("*")
    ],
    OP2N.builder("Div", "L1", (" / ", "SLASH"), "L2"),
    OP2N.builder("Add", "L0", (" + ", "PLUS"), "L1"),
    OP2N.builder("Sub", "L0", (" - ", "MINUS"), "L1"),
    # ENUMS
    EnumN.builder("Args", "L0", COMMA, backward=True),
    EnumN.builder("Equations", "L-1", ("\n", "NEWLINE"), backward=True),
    # UNITS
    [Id, match("ID").in_("*")],
    [Integer, match("INT").in_("*")],
    [Decimal, match("FLOAT").in_("*")],
    pattern_libs=["maths", "blocs", "units"]

)

lexer.add_pattern("NEWLINE.SYMBOL", mode="str", expr="\n")
lexer.add_pattern("COMMA.SYMBOL", mode="str", expr=",")

lexer.add_pattern("INT.SQR.POWER", mode="str", expr="²", value=2)
lexer.add_pattern("INT.CUBE.POWER", mode="str", expr="³", value=3)

parser.add_routine("L-1", match("Attr") | match("L0"))
parser.add_routine("L0", match("Add") | match("Sub") | match("L1"))
parser.add_routine("L1", match("Mul") | match("Div") | match("L2"))
parser.add_routine("L2", match("Pow") | match("L3"))
parser.add_routine("L3", match("Call") | match("Id") | match("Integer") | match("Decimal") | match("BlocP"))

parser.add_routine("default", match("L-1"))


class Tester:
    def __init__(self, **functions):
        self.functions = functions

    def add(self, name, func):
        self.functions[name] = func

    def __call__(self, *args, **kwargs):
        result = {}
        for name, func in self.functions.items():
            ti = time.time()
            func(*args, **kwargs)
            tf = time.time()
            dt = tf - ti
            result[name] = dt

        return result

    def improvement(self, name, *args, **kwargs):
        """Calculate the improvement made by each function compared to the specified one"""

        result = self(*args, **kwargs)
        dt = result.get(name)
        return dict((name_, int(100 * (dt - dt_) / dt)) for name_, dt_ in result.items() if name != name_)


o_engine = optimize(engine)


def unoptimized(text):
    return engine.read(text, identifier="default", backward=True)


def optimized(text):
    return o_engine.read(text, identifier="default", backward=True)


tester = Tester(
    unoptimized=unoptimized,
    optimized=optimized
)

if __name__ == "__main__":
    text = """y = 3 * x ^ 2 + 1 - 6 + 4
t = x² + y² + z²
u = 2x - 3y + 7z
v = 10x-6.7z + 1.001y
y = f(x, y, z)"""
    # text = "f(x, x, x) * f(y, y, y) ^ f(z, z, z)"
    # text = "(x+y+z)"
    text = """y = 5f(x²)-12x/(1+x)³-2"""

    # with open("base_engine.txt", mode="w", encoding="utf-8") as file:
    #     file.write("\n".join(map(str, engine.parser.builders)))
    #
    # with open("opti_engine.txt", mode="w", encoding="utf-8") as file:
    #     file.write("\n".join(map(str, o_engine.parser.builders)))

    print()
    print(repr(unoptimized(text)))

    print()
    print(repr(optimized(text)))

    display(engine.result(text, identifier="default", backward=True), no_keys=True, no_unused_matches=True)

    from tkinter import *
    from CurvePlot import CurvePlot

    T_MAX = 100

    tk = Tk()
    tk.geometry("400x400")

    cp = CurvePlot(tk, 0, -100, T_MAX, 100, bg="black", highlightthickness=0)
    cp.pack(side=TOP, fill=BOTH, expand=True)

    cp.itemconfigure(cp.line, fill="lime")
    cp.itemconfigure(cp.mean, fill="orange")
    cp.itemconfigure(cp.zero, fill="blue")


    def run(ms, t, n):
        cp.coords(cp.zero, 0, cp.winfo_height() // 2, cp.winfo_width(), cp.winfo_height() // 2)
        for name, percent in tester.improvement("unoptimized", text=text).items():
            cp.feed(t, percent)
            print(f"{name} -> {percent}%")
            break

        if n > 0:
            tk.after(ms, run, ms, t + 1, n - 1)


    run(20, 0, T_MAX)

    tk.mainloop()

    # for _ in range(10):
    #     for name, percent in tester.improvement("unoptimized", text=text).items():
    #         print(f"{name} -> {percent}%")
    #
    # print()
    # print(unoptimized(text))
    #
    # print()
    # print(optimized(text))
