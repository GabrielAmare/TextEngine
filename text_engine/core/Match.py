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

    def parse(self, tokens: List[Token], position: int, parser: Parser):
        if 0 <= position < len(tokens):
            token = tokens[position]
            if token.pattern <= self.identifier:
                result = MatchResult(rule=self, token=token)
                return result

            for builder in parser.get_all_matching_builders(self.identifier):
                result = builder.parse(tokens, position, parser)
                if result:
                    return result

            return Result_Error(
                rule=self,
                at_position=position,
                reason=f"No matching pattern, routine or builder for {repr(self.identifier)} on {repr(token.pattern.identifier)}"
            )
        else:
            return Result_Error(
                rule=self,
                at_position=position,
                reason="No token remaining"
            )


class MatchResult(Result):
    def __init__(self, rule: Rule, token: Token):
        super().__init__(rule, token.at_position, token.to_position)
        self.token = token

    def __str__(self):
        return super().__str__() + "(" + self.token.pattern.name + " -> " + repr(self.token.value) + ")"

    def build(self, context: Context):
        context.add_item(self.token.value)
