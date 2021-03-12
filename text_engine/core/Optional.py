from ..base import Rule_Unit, Result_List
from .Parser import Parser


class Optional(Rule_Unit):
    def parse(self, tokens: list, position: int, parser: Parser, backward: bool = False):
        results = OptionalResult(rule=self, at_position=position)

        result = self.rule.parse(tokens, position, parser, backward)

        if result:
            results.append(result, backward)

        return results


class OptionalResult(Result_List):
    pass
