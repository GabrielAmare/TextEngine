from typing import Tuple, List, Dict, Type, Union, Callable
import python_generator as pg
from item_engine import Branch, Group, Rule
from .items import *
from .functions import *
from .base_materials import *
from .operators import OP, UNIT, ENUM

__all__ = [
    "digits", "digits_pow", "digits_bin", "digits_oct", "digits_hex",
    "letters", "LETTERS", "alpha", "alphanum",
    "dot",
    "n_alphanum",
    "sq", "dq", "n_sq", "n_dq", "e_sq", "e_dq",

    "gen_symbols", "gen_keywords", "gen_branches", "gen_operators",
    "GroupMaker",
    "MakeLexer", "MakeParser",
    "INT_POW_TO_INT"
]

digits = charset("0123456789").inc()
digits_pow = charset("⁰¹²³⁴⁵⁶⁷⁸⁹").inc()
digits_bin = charset("01").inc()
digits_oct = charset("01234567").inc()
digits_hex = charset('0123456789' + 'abcdef' + 'ABCDEF').inc()

letters = charset('abcdefghijklmnopqrstuvwxyz').inc()
LETTERS = charset('ABCDEFGHIJKLMNOPQRSTUVWXYZ').inc()
alpha = charset('abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + '_').inc()
alphanum = charset('abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + '_' + '0123456789').inc()

dot = charset(".").inc()

n_alphanum = (~alphanum.group).inc()

sq = charset("'").inc()
dq = charset('"').inc()

n_sq = (~sq.group).inc()
n_dq = (~dq.group).inc()
e_sq = string("\\'")
e_dq = string('\\"')


class GroupMaker:
    def __init__(self, data: Dict[str, List[str]]):
        self.data: Dict[str, List[str]] = data

    def __getitem__(self, name: str) -> Group:
        if name not in self.data:
            return TokenG.grp([name])

        result: List[str] = []
        todo: List[str] = [name]
        index = 0
        while index < len(todo):
            name = todo[index]
            if name in self.data:
                for val in self.data[name]:
                    if val not in self.data:
                        result.append(val)
                        continue

                    if val not in todo:
                        todo.append(val)

            index += 1

        return TokenG.grp(result)


class SymbolMaker:
    def __init__(self, **names):
        self.names = {v: k for k, v in names.items()}

    def __call__(self, expr: str) -> Symbol:
        ls = len(expr) - len(expr.lstrip(' '))
        rs = len(expr) - len(expr.rstrip(' '))
        expr = expr.strip(' ')
        return Symbol(name="_".join(map(self.names.__getitem__, expr)), expr=expr, ls=ls, rs=rs)


symbol_maker = SymbolMaker(
    EQUAL="=", PLUS="+", DASH="-", STAR="*", SLASH="/", UNSC="_", VBAR="|", AMPS="&",
    SHARP="#", AT="@", HAT="^", PERCENT="%", WAVE="~", CSLASH="\\",
    COMMA=",", DOT=".", EXC="!", INTER="?", COLON=":", SEMICOLON=";",
    LV="<", RV=">", LP="(", RP=")", LB="[", RB="]", LS="{", RS="}", DQ='"', SQ="'",
    DOLLAR="$", EURO="€", POUND="£", NEWLINE='\n',
    POW0="⁰", POW1="¹", POW2="²", POW3="³", POW4="⁴", POW5="⁵", POW6="⁶", POW7="⁷", POW8="⁸", POW9="⁹",
    # Maths Sets Symbols
    FORALL="∀", EXIST="∃", ISIN="∈", NOTIN="∉", NI="∋",
    CAP="∩", CUP="∪", SUB="⊂", SUP="⊃", NSUB="⊄", SUBE="⊆", SUPE="⊇",
    # Maths Logic Symbols
    AND="∧", OR="∨", EQUIV="≡", THERE4="∴", OPLUS="⊕", OTIMES="⊗", PERP="⊥", LOZ="◊",
    # Other Misc Maths Symbols
    PART="∂", EMPTY="∅", NABLA="∇", PROD="∏", SUM="∑", MINUS="−", LOWAST="∗", RADIC="√", SDOT="⋅",
    PROP="∝", INFIN="∞", ANG="∠", INT="∫", SIM="∼", CONG="≅", ASYMP="≈", NE="≠", LE="≤", GE="≥",
)
_POW_INT_CHARS = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9"}
_POW_INT_ORDS = {ord(k): ord(v) for k, v in _POW_INT_CHARS.items()}

INT_POW_TO_INT = pg.LAMBDA(
    args=["content"],
    expr=pg.CALL(
        name="content.translate",
        args=pg.ARGS(pg.DICT(_POW_INT_ORDS))
    )
)


# INT_POW_TO_INT = "lambda content: content.translate(" \
#                  "{8304: 48, 185: 49, 178: 50, 179: 51, 8308: 52, 8309: 53, 8310: 54, 8311: 55, 8312: 56}" \
#                  ")"


def gen_symbols(*exprs: str) -> Tuple[List[Branch], Dict[str, TokenI], Dict[str, Symbol]]:
    branches: List[Branch] = []
    symbols: Dict[str, TokenI] = {}
    raw_symbols: Dict[str, Symbol] = {}
    for symbol in map(symbol_maker, exprs):
        branches.append(symbol.branch)
        symbols[symbol.name] = symbol.tokenI
        raw_symbols[symbol.expr] = symbol

    return branches, symbols, raw_symbols


def gen_keywords(*exprs: str) -> Tuple[List[Branch], Dict[str, TokenI], Dict[str, Keyword]]:
    branches = []
    keywords = {}
    raw_keywords: Dict[str, Keyword] = {}

    for expr in exprs:
        ls = len(expr) - len(expr.lstrip(' '))
        rs = len(expr) - len(expr.rstrip(' '))
        expr = expr.strip(' ')

        keyword = Keyword(expr=expr, ls=ls, rs=rs)
        branches.append(keyword.branch)
        keywords[keyword.name] = keyword.tokenI
        raw_keywords[keyword.name] = keyword

    return branches, keywords, raw_keywords


def gen_branches(**config) -> List[Branch]:
    return [Branch(name=key, rule=val) for key, val in config.items()]


def gen_operators(**data: Dict[str, Union[UNIT, OP, ENUM]]) -> Tuple[List[Branch], pg.MODULE]:
    branches: List[Branch] = []

    classes_operators: List[pg.CLASS] = []
    ifs_operators: List[pg.IF] = []

    classes_units: List[pg.CLASS] = []
    ifs_units: List[pg.IF] = []

    op_type: Type[Union[OP, UNIT, ENUM]]

    for cls_name, obj in data.items():
        if isinstance(obj, UNIT):
            classes_units.append(obj.pg_class(cls_name))
            ifs_units.append(obj.pg_if(cls_name))
        elif isinstance(obj, (OP, ENUM)):
            branches.append(obj.branch(cls_name))
            classes_operators.append(obj.pg_class(cls_name))
            ifs_operators.append(obj.pg_if(cls_name))
        else:
            raise ValueError(obj)

    return branches, pg.MODULE([
        pg.FROM_IMPORT("item_engine.textbase", pg.ARGS("*")),
        *classes_units,
        *classes_operators,
        pg.DEF(
            name="build",
            args=pg.ARGS(pg.ARG('e', t='Element')),
            body=pg.SWITCH(ifs=[
                pg.IF(
                    cond=pg.ISINSTANCE('e', t='Lemma'),
                    body=pg.SWITCH(
                        ifs=ifs_operators,
                        default=pg.RAISE(pg.EXCEPTION('e.value'))
                    )
                ),
                pg.IF(
                    cond=pg.ISINSTANCE('e', t='Token'),
                    body=pg.SWITCH(
                        ifs=ifs_units,
                        default=pg.RAISE(pg.EXCEPTION('e.value'))
                    )
                )
            ], default=pg.RAISE(pg.EXCEPTION('e.value'))
            )
        )
    ])


def MakeLexer(
        keywords: List[str] = None,
        symbols: List[str] = None,
        branches: Dict[str, Rule] = None
):
    if keywords is None:
        keywords = []
    if symbols is None:
        symbols = []
    if branches is None:
        branches = {}
    keyword_b, KW, keyword_register = gen_keywords(*keywords)

    symbols_b, SYM, symbols_register = gen_symbols(*symbols)

    lexer = make_branch_set(
        *keyword_b,
        *symbols_b,
        *gen_branches(**branches)
    )

    return lexer, keyword_register, symbols_register


def MakeParser(
        operators: Dict[str, Union[UNIT, OP, ENUM]] = None,
        branches: Dict[str, Rule] = None
):
    if operators is None:
        operators = {}
    if branches is None:
        branches = {}

    operators_b, op_register = gen_operators(**operators)

    parser = make_branch_set(
        *operators_b,
        *gen_branches(
            **branches
        )
    )

    return parser, op_register
