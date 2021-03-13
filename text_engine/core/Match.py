from ..base import Rule, Identified, Result, Context, Result_Error
from .Token import Token
from .Parser import Parser
from typing import List


class Match(Rule, Identified):
    def __init__(self, identifier: str):
        Rule.__init__(self)
        Identified.__init__(self, identifier)

    def __str__(self):
        return self.__class__.__name__ + "(" + self.identifier + ")"

    def parse(self, tokens: List[Token], position: int, parser: Parser, backward: bool = False):
        t_position = position - 1 if backward else position
        if 0 <= t_position < len(tokens):
            token = tokens[t_position]
            if token.pattern <= self.identifier:
                result = MatchResult(rule=self, token=token)
                return result

            count = 0
            result = None
            for builder in parser.get_all_matching_builders(self.identifier):
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


class MatchResult(Result):
    def __init__(self, rule: Rule, token: Token):
        super().__init__(rule, token.at_position, token.to_position, layer=1)
        self.token = token

    def __str__(self):
        return super().__str__() + "(" + self.token.pattern.name + " -> " + repr(self.token.value) + ")"

    def build(self, context: Context):
        context.add_item(self.token.value)
