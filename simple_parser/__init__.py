from item_engine.textbase import *

lexer, kws, sym = MakeLexer(
    keywords=[],
    symbols=[],
    branches=dict(
        ID=alpha & alphanum.repeat(0, INF),
        INT=digits.repeat(1, INF),
        FLOAT=digits.repeat(1, INF) & dot & digits.repeat(0, INF)
              | dot & digits.repeat(1, INF),
    )
)

engine = Engine(
    name="basic",
    parsers=[
        Parser(
            name='lexer',
            branch_set=lexer,
            input_cls=Char,
            output_cls=Token,
            skips=["WHITESPACE"],
            reflexive=False,
            formal=True,
        ),
    ]
)

engine.build()
