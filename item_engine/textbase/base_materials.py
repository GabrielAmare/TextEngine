from item_engine.base import Branch
from .functions import string
from .items import TokenI, TokenG

__all__ = ["Symbol", "Keyword", "Helper"]


class Helper:
    branch: Branch
    tokenI: TokenI
    tokenG: TokenG

    def __init__(self, name: str, expr: str, ls: int = 0, rs: int = 0):
        self.name: str = name
        self.expr: str = expr
        self.ls: int = ls
        self.rs: int = rs

    def __str__(self):
        return self.ls * ' ' + self.expr + self.rs * ' '


class Symbol(Helper):
    def __init__(self, name: str, expr: str, ls: int = 0, rs: int = 0):
        super().__init__(name=name, expr=expr, ls=ls, rs=rs)

        self.branch: Branch = Branch(
            name=self.name,
            rule=string(self.expr),
            priority=100 + len(self.expr)
        )
        self.tokenI: TokenI = TokenI(name=self.name)
        self.tokenG: TokenG = self.tokenI.as_group


class Keyword(Helper):
    def __init__(self, expr: str, ls: int = 0, rs: int = 0):
        super().__init__(name=expr.upper(), expr=expr, ls=ls, rs=rs)
        self.branch: Branch = Branch(
            name=f"KW_{self.name}",
            rule=string(self.expr),
            priority=200
        )
        self.tokenI: TokenI = TokenI(name=f"KW_{self.name}")
        self.tokenG: TokenG = self.tokenI.as_group
