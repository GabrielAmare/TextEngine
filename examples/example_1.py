from text_engine import *

lexer = Lexer()
parser = Parser()

engine = Engine(lexer, parser)

lexer.add_pattern("LP", mode="str", expr="(")
lexer.add_pattern("RP", mode="str", expr=")")
lexer.add_pattern("LB", mode="str", expr="[")
lexer.add_pattern("RB", mode="str", expr="]")
lexer.add_pattern("LV", mode="str", expr="<")
lexer.add_pattern("RV", mode="str", expr=">")
lexer.add_pattern("LS", mode="str", expr="{")
lexer.add_pattern("RS", mode="str", expr="}")

lexer.add_pattern("COMA", mode="str", expr=",")

lexer.add_pattern("VAR", mode="re", expr="[a-zA-Z_][a-zA-Z0-9_]*")
lexer.add_pattern("INT", mode="re", expr="[0-9]+", value=int)

lexer.add_pattern("WHITESPACE", mode="re", expr="[ \t\n]+", flag=16, ignore=True, priority=1000)
lexer.add_pattern("ERROR", mode="re", expr=".+", flag=16, priority=1000)

parser.add_routine("INT_ENUM", match("INT").in_("items").sep_by("COMA"))

parser.add_builder("INT_TUPLE", match("INT_ENUM").wrapped_by("LP", "RP"))
parser.add_builder("INT_LIST", match("INT_ENUM").wrapped_by("LB", "RB"))

if __name__ == '__main__':
    ast = engine.read("[1, 2, 3, 4, 5, 6]")

    print(ast)
