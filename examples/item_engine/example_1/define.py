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
        FLOAT=digits.repeat(1, INF) & dot & digits.repeat(0, INF) | dot & digits.repeat(1, INF),
    )

)

grp = GroupMaker({
    "unit": ["VAR", "INT", "FLOAT", "__PAR__"],
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
        Float=UNIT(n="FLOAT", k="value", t=float),
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
        __MUL__=(grp["INT"].as_("c0") | grp["FLOAT"].as_("c0")) & grp["power"].as_("c1"),
        __POW__=grp["power"].as_("c0") & grp["INT_POW"].as_("c1"),
    )
)

engine = Engine(
    name='maths',
    parsers=[
        Parser(
            name='lexer',
            branch_set=lexer,
            input_cls=Char,
            output_cls=Token,
            skips=["WHITESPACE"],
            formal_inputs=True,
            formal_outputs=True,
            reflexive=False,
        ),
        Parser(
            name='parser',
            branch_set=parser,
            input_cls=Token,
            output_cls=Lemma,
            skips=[],
            formal_inputs=True,
            formal_outputs=False,
            reflexive=True,
        )
    ],
    operators=operators
)
