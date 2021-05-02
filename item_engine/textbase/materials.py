from typing import Tuple, List, Dict

from item_engine import Branch
from .items import *
from .functions import *

__all__ = [
    "digits", "digits_pow", "digits_bin", "digits_oct", "digits_hex",
    "letters", "LETTERS", "alpha", "alphanum",
    "dot",
    "n_alphanum",
    "sq", "dq", "n_sq", "n_dq", "e_sq", "e_dq",

    "gen_symbols", "gen_keywords", "gen_branches"
]

digits = charset("0123456789").match("include")
digits_pow = charset("⁰¹²³⁴⁵⁶⁷⁸⁹").match("include")
digits_bin = charset("01").match("include")
digits_oct = charset("01234567").match("include")
digits_hex = charset('0123456789' + 'abcdef' + 'ABCDEF').match("include")

letters = charset('abcdefghijklmnopqrstuvwxyz').match("include")
LETTERS = charset('ABCDEFGHIJKLMNOPQRSTUVWXYZ').match("include")
alpha = charset('abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + '_').match("include")
alphanum = charset('abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + '_' + '0123456789').match("include")

dot = charset(".").match("include")

n_alphanum = (~alphanum.group).match("include")

sq = charset("'").match("include")
dq = charset('"').match("include")

n_sq = (~sq.group).match("include")
n_dq = (~dq.group).match("include")
e_sq = string("\\'")
e_dq = string('\\"')


class Symbol:
    def __init__(self, name: str, expr: str):
        self.name = name
        self.expr = expr

    @property
    def branch(self) -> Branch:
        return Branch(
            name=self.name,
            rule=string(self.expr),
            priority=100 + len(self.expr)
        )

    @property
    def tokenI(self) -> TokenI:
        return TokenI(name=self.name).as_group


class Keyword:
    def __init__(self, expr: str):
        self.raw_name = expr.upper()
        self.expr = expr

    @property
    def branch(self) -> Branch:
        return Branch(
            name=f"KW_{self.raw_name}",
            rule=string(self.expr),
            priority=200
        )

    @property
    def tokenI(self) -> TokenI:
        return TokenI(name=f"KW_{self.raw_name}").as_group


class SymbolMaker:
    def __init__(self, **names):
        self.names = {v: k for k, v in names.items()}

    def __call__(self, expr: str) -> Symbol:
        return Symbol(name="_".join(map(self.names.__getitem__, expr)), expr=expr)


symbol_maker = SymbolMaker(
    EQUAL="=", PLUS="+", DASH="-", STAR="*", SLASH="/", UNSC="_", VBAR="|", AMPS="&",
    SHARP="#", AT="@", HAT="^", PERCENT="%", WAVE="~", CSLASH="\\",
    COMMA=",", DOT=".", EXC="!", INT="?", COLON=":", SEMICOLON=";",
    LV="<", RV=">", LP="(", RP=")", LB="[", RB="]", LS="{", RS="}", DQ='"', SQ="'",
    DOLLAR="$", EURO="€", POUND="£",
    POW0="⁰", POW1="¹", POW2="²", POW3="³", POW4="⁴", POW5="⁵", POW6="⁶", POW7="⁷", POW8="⁸", POW9="⁹",
)


def gen_symbols(*exprs: str) -> Tuple[List[Branch], Dict[str, TokenI]]:
    branches = []
    symbols = {}
    for symbol in map(symbol_maker, exprs):
        branches.append(symbol.branch)
        symbols[symbol.name] = symbol.tokenI

    return branches, symbols


def gen_keywords(*exprs: str) -> Tuple[List[Branch], Dict[str, TokenI]]:
    branches = []
    keywords = {}

    for expr in exprs:
        keyword = Keyword(expr)
        branches.append(keyword.branch)
        keywords[keyword.raw_name] = keyword.tokenI

    return branches, keywords


def gen_branches(**config) -> List[Branch]:
    return [Branch(name=key, rule=val) for key, val in config.items()]
