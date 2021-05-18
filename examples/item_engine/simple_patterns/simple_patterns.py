from item_engine.textbase import *

INT = Parser(
    name='INT',
    branch_set=MakeLexer(
        branches=dict(
            INT=digits.repeat(1, INF),
        )

    )[0],
    input_cls=Char,
    output_cls=Token,
    skips=["WHITESPACE"],
    reflexive=False,
    formal=True,
)

FLOAT1 = Parser(
    name='FLOAT1',
    branch_set=MakeLexer(
        branches=dict(
            FLOAT=dot & digits.repeat(1, INF),
        )

    )[0],
    input_cls=Char,
    output_cls=Token,
    skips=["WHITESPACE"],
    reflexive=False,
    formal=True,
)

FLOAT2 = Parser(
    name='FLOAT2',
    branch_set=MakeLexer(
        branches=dict(
            FLOAT=digits.repeat(1, INF) & dot & digits.repeat(0, INF),
        )

    )[0],
    input_cls=Char,
    output_cls=Token,
    skips=["WHITESPACE"],
    reflexive=False,
    formal=True,
)

print(INT.table)
print(FLOAT1.table)
print(FLOAT2.table)

# INT.graph.display()
# FLOAT1.graph.display()
# FLOAT2.graph.display()
