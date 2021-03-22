from ...base import *
from ...core import *
from ...core.results import *
from typing import List


class Optimized_Match(Match):
    def __init__(self, identifier: str, patterns, builders):
        super().__init__(identifier)
        self.patterns = patterns
        self.builders = builders

    def __str__(self):
        return "Match(" + "|".join(pattern.identifier for pattern in (*self.patterns, *self.builders)) + ")"

    def parse(self, tokens: List[Token], position: int, parser: Parser, backward: bool = False):
        t_position = position - 1 if backward else position
        if 0 <= t_position < len(tokens):
            token = tokens[t_position]
            if token.pattern in self.patterns:
                result = MatchResult(rule=self, token=token)
                return result

            count = 0
            result = None
            for builder in self.builders:
                result = builder.parse(tokens, position, parser, backward)
                if result:
                    return result
                else:
                    count += 1

            return Result_Error(
                rule=self,
                at_position=position,
                reason=f"Token {repr(token.pattern.identifier)} doesn't match {repr(self.identifier)}"
                       f", {count} routine or builder correponding to {repr(self.identifier)} (no match)",
                result=result if count == 1 else None
            )
        else:
            return Result_Error(
                rule=self,
                at_position=position,
                reason="No token remaining"
            )
