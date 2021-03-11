from .core import *


def base(*cls_rules):
    lexer = Lexer()

    lexer.add_pattern("WHITESPACE", mode="re", expr="[ \t\n]+", flag=16, ignore=True, priority=1000)
    lexer.add_pattern("ERROR", mode="re", expr=".+", flag=16, priority=1000)

    parser = Parser()

    classes = set()
    for cls, *rules in cls_rules:
        classes.add(cls)
        for rule in rules:
            parser.add_builder(cls.__name__, rule)

    builder = ASTB(*classes)

    engine = Engine(lexer, parser, builder)

    return lexer, parser, builder, engine
