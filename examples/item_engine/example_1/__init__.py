from item_engine.textbase import *

lexer, kws, sym = MakeLexer(
    keywords=[
        ' and ', ' or ', 'not '
    ],
    symbols=[
        ' + ', ' - ', ' / ', ' * ', ' ^ ',  # operations
        ' == ', ' < ', ' <= ', ' > ', ' >= ',  # comparisons
        '=',  # attributions
        '( ', ' )',  # parenthesis
        '{ ', ' }',  # splines
        '\n', ', ',  # separators
        ' | ', ' & ', '!',
        '∀', '∃', ' ∈ ', ' ∉ '
    ],
    branches=dict(
        WHITESPACE=charset(" \t").inc().repeat(1, INF),
        NEWLINE=charset('\n').inc().repeat(1, INF),
        VAR=alpha & alphanum.repeat(0, INF),
        INT=digits.repeat(1, INF),
        INT_POW=digits_pow.repeat(1, INF),
        FLOAT=digits.repeat(1, INF) & dot & digits.repeat(0, INF)
              | dot & digits.repeat(1, INF),
    )

)

grp = GroupMaker({
    "unit": ["VAR", "INT", "__PAR__"],
    "power": ["__POW__", "unit"],
    "neg": ["__NEG__", "power"],
    "term": ["__MUL__", "__DIV__", "neg"],
    "expr": ["__ADD__", "__SUB__", "term"],

    "comp": ["__EQ__", "__LT__", "__LE__", "__GT__", "__GE__", "expr"],

    "not": ["__NOT__", "comp"],
    "and": ["__AND__", "not"],
    "or": ["__OR__", "and"],

    "set": ["__SET__", "VAR"],
})

parser, operators = MakeParser(
    operators=dict(
        ForAll=OP(sym["∀"], grp["VAR"], sym['∈'], grp["VAR"]),
        Exists=OP(sym["∃"], grp["VAR"], sym['∈'], grp["VAR"]),
        Constraint=OP(grp["__FORALL__"], sym[','], grp["__EXISTS__"], sym['|'], grp["or"]),

        EnumV=ENUM(grp["unit"], sym[","]),
        Set=OP(sym['{'], grp["__ENUMV__"], sym['}']),

        Var=UNIT(n="VAR", k="name", t=str),
        Int=UNIT(n="INT", k="value", t=int),
        IntPow=UNIT(n="INT_POW", k="value", t=int, f=INT_POW_TO_INT),

        Pow=OP(grp["power"], sym["^"], grp["unit"]),

        Neg=OP(sym["-"], grp["neg"]),

        Mul=OP(grp["term"], sym["*"], grp["neg"]),
        Div=OP(grp["term"], sym["/"], grp["neg"]),

        Add=OP(grp["expr"], sym["+"], grp["term"]),
        Sub=OP(grp["expr"], sym["-"], grp["term"]),

        Eq=OP(grp["comp"], sym["=="], grp["expr"]),
        Lt=OP(grp["comp"], sym["<"], grp["expr"]),
        Le=OP(grp["comp"], sym["<="], grp["expr"]),
        Gt=OP(grp["comp"], sym[">"], grp["expr"]),
        Ge=OP(grp["comp"], sym[">="], grp["expr"]),

        Not=OP(kws["NOT"], grp["not"]),
        And=OP(grp["and"], kws["AND"], grp["not"]),
        Or=OP(grp["or"], kws["OR"], grp["and"]),

        Attr=OP(grp["VAR"], sym["="], grp["or"]),
        Par=OP(sym["("], grp["or"], sym[")"]),

        Equations=ENUM(grp["__ATTR__"], sym["\n"]),
    ),
    branches=dict(
        __MUL__=grp["INT"].as_("c0") & grp["VAR"].as_("c1"),
        __POW__=grp["VAR"].as_("c0") & grp["INT_POW"].as_("c1"),
    )
)

engine = Engine(
    name='maths',
    parsers=[
        Parser(
            name='lexer',
            branch_set=lexer,
            formal=True,
        ),
        Parser(
            name='parser',
            branch_set=parser,
            reflexive=True,
        )
    ],
    operators=operators
)

for parser in engine.parsers:
    parser.l6.graph.display()
    # parser.l6.to_csv(parser.name)

engine.build(
    allow_overwrite=True
)

from examples.item_engine.example_1.maths import gen_networks

lexer, parser = gen_networks(
    lexer_cfg=dict(
        input_cls=Char,
        output_cls=Token,
        to_ignore=["WHITESPACE"],
        allow_gaps=True,
        save_terminals=True,
        remove_previous=False
    ),
    parser_cfg=dict(
        input_cls=Token,
        output_cls=Lemma,
        to_ignore=[],
        allow_gaps=True
    )
)

from examples.item_engine.example_1.maths.materials import *


def parse_text(text: str):
    lexer, parser = gen_networks(
        lexer_cfg=dict(
            input_cls=Char,
            output_cls=Token,
            to_ignore=["WHITESPACE"],
            allow_gaps=True,
            save_terminals=True,
            remove_previous=False
        ),
        parser_cfg=dict(
            input_cls=Token,
            output_cls=Lemma,
            to_ignore=[],
            allow_gaps=True
        )
    )
    characters = make_characters(text)
    lexer.feed_iterator(characters)
    parser.feed_network(lexer)

    for item in parser:
        pass

    positions = parser.pr.positions
    mn, mx = min(positions), max(positions)

    for final in parser.terminals:
        if parser.pr.get(final.at) == mn:
            if parser.pr.get(final.to) == mx:
                yield build(final)


# characters = make_characters("x := y + 2\ny := x / 5 - y")
characters = make_characters("∀ x ∈ X, ∃ y ∈ Y | x + y == 5 and x * y == 6")
# characters = make_characters("{1, 2, 3, x}")
lexer.feed_iterator(characters)
parser.feed_network(lexer)

for item in parser:
    pass


def get_content(o: Lemma) -> str:
    return '\n'.join(
        '\n'.join(
            f"{key!s}[{index}]: {item.value} = {str(item) if isinstance(item, Token) else '...'}"
            for index, item in enumerate(val)
        )
        if isinstance(val, list) else
        f"{key!s}: {val.value} = {str(val) if isinstance(val, Token) else '...'}"
        for key, val in o.data.items()
    )


print(lexer.terminal_table(content=str))
print(parser.terminal_table(content=get_content))

positions = parser.pr.positions
mn, mx = min(positions), max(positions)

for final in parser.terminals:
    if parser.pr.get(final.at) == mn:
        if parser.pr.get(final.to) == mx:
            print()
            print(build(final))
            print()
            print(repr(build(final)))
            print()

print(mn, mx)

# SHOW LENGTH OF THE GENERATED FILES
from tools37 import TextFile

TextFile.extension = ".py"
for fp in ["maths/__init__.py", "maths/lexer.py", "maths/parser.py", "maths/materials.py"]:
    length = len(TextFile.load(fp).split('\n'))
    print(f"{fp!r} : {length} lines")

texts = [
    "∀ x ∈ X, ∃ y ∈ Y | x + y == 5 and x * y == 6",
    "{1, 2, 3, x}"
]
for text in texts:
    print(f"\ntext:\n\t{text!r}\nresults:")
    for index, obj in enumerate(parse_text(text)):
        print(f"\t[{index}] {obj!r}")
