from text_engine import *

lexer, parser, builder, engine = base(pattern_libs=["blocs", "units"])

lexer.add_pattern("COMMA", mode="str", expr=",")

parser.add_routine("INT_ENUM", match("INT").in_("items").sep_by("COMMA", backward=True))

parser.add_builder("INT_TUPLE", match("INT_ENUM").wrapped_by("LP", "RP"))
parser.add_builder("INT_LIST", match("INT_ENUM").wrapped_by("LB", "RB"))

if __name__ == '__main__':
    ast = engine.read("[1, 2, 3, 4, 5, 6]", backward=True)
    print(ast)

    ast = engine.read("(0, 15678, 95, 484876, 05959595)", backward=True)
    print(ast)
