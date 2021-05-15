from tools37 import CsvFile

from item_engine.textbase import MakeLexer, string, Engine, Parser

REMOVE_COMPOSED = True


def extract_mood(code: str) -> str:
    return code.split('-')[2]


def extract_tense(code: str) -> str:
    return code.split('-')[3]


def extract_sign(code: str) -> str:
    return code.split('-')[3]


data = [(row['expr'], extract_mood(row['code'])) for row in CsvFile.load("conj_file.csv") if
        not REMOVE_COMPOSED or ' ' not in row['expr']]


lexer, kws, sym = MakeLexer(
    keywords=[],
    symbols=[],
    branches={code: string(expr) for expr, code in data}

)

print('lexer made')

engine = Engine(
    name='conjugation',
    parsers=[
        Parser(
            name='mood_lexer',
            branch_set=lexer
        )
    ]
)

print('engine made')
print(f"{len(engine.parsers[0].branch_sets)} branch sets to generate")

engine.build(
    allow_overwrite=True
)

print('package built')

for parser in engine.parsers:
    parser.get_code.graph.display()
