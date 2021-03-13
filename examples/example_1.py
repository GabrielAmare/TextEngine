from text_engine import *

lexer, parser, builder, engine = base(pattern_libs=["blocs", "units"])

lexer.add_pattern("COMMA.SYMBOL", mode="str", expr=",")

parser.add_routine("INT_ENUM", match("INT").in_("items").sep_by("COMMA", backward=True))

parser.add_builder("INT_TUPLE", match("INT_ENUM").wrapped_by("LP", "RP"))
parser.add_builder("INT_LIST", match("INT_ENUM").wrapped_by("LB", "RB"))

if __name__ == '__main__':
    ast = engine.read("[1, 2, 3, 4, 5, 6]", backward=True)
    print(ast)

    ast = engine.read("(0, 15678, 95, 484876, 05959595)", backward=True)
    print(ast)

    chart = {
        "*": dict(bg="black", fg="white", bd=2, relief="sunken", font=("Consolas", 12, "bold"), padx=5, pady=5),
        "ID": dict(fg="red"),
        "INT": dict(fg="blue"),
        "FLOAT": dict(fg="blue"),
        "*.SYMBOL": dict(fg="orange"),
        "*.POWER": dict(fg="purple"),
    }
    text = "(0, 15678, 95, 484876, 05959595)"


    app = tkEngine(engine, text, chart, backward=True)

    app.mainloop()
