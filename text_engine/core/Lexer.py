from .Pattern import Pattern
from typing import List


class TokenizeError(Exception):
    pass


class Lexer:
    patterns: List[Pattern]

    def __init__(self, *patterns: Pattern):
        self.patterns = list(patterns)

    def i_tokenize(self, text: str, index=0, position=0):
        length = len(text) - index
        while index < length:
            for pattern in sorted(self.patterns, key=lambda pattern: pattern.priority):
                token = pattern.tokenize(text, index, position)
                if token:
                    if not pattern.ignore:
                        yield token
                        position = token.to_position
                    index = token.to_index
                    break
            else:
                raise TokenizeError(repr(text[index:]))

    def tokenize(self, text, index=0, position=0):
        return list(self.i_tokenize(text, index, position))

    def add_pattern(self, identifier, mode, expr, flag=0, ignore=False, value=None, priority=0):
        raise NotImplementedError
