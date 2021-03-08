from re import compile
from .Token import Token
from ..base import Identified


class Pattern(Identified):
    mode: str
    expr: str
    flag: int
    ignore: bool
    value: (object, callable)
    priority: (int, float)

    def __init__(self, identifier: str, mode: str, expr: str,
                 flag: int = 0, ignore: bool = False, value=None, priority: int = 0):
        super().__init__(identifier)

        self.mode = mode
        self.expr = expr
        self.flag = flag
        self.ignore = ignore
        self.value = value
        self.priority = priority

        if self.mode == "re":
            self.regex = compile(pattern=self.expr, flags=self.flag)
        elif self.mode == "kw":
            self.regex = compile(pattern=r"(?<!\w)(" + self.expr + r")(?!\w)", flags=self.flag)
        else:
            self.regex = None

    def make_token(self, content, at_index, at_position):
        if self.value is None:
            value = content
        elif hasattr(self.value, "__call__"):
            value = self.value(content)
        else:
            value = self.value

        return Token(
            pattern=self,
            content=content,
            at_index=at_index,
            at_position=at_position,
            value=value
        )

    def tokenize(self, text: str, index: int, position: int):
        content = ""
        if self.regex:
            match = self.regex.match(text, index)
            if match:
                content = match.group()
        else:
            if text.startswith(self.expr, index):
                content = self.expr

        if content:
            return self.make_token(content, index, position)
