from ..base import Rule_Unit, Result_List
from .Parser import Parser


class Optional(Rule_Unit):
    def parse(self, tokens: list, position: int, parser: Parser):
        results = OptionalResult(rule=self, at_position=position)

        result = self.rule.parse(tokens, position, parser)

        if result:
            results.append(result)

        return results


class OptionalResult(Result_List):
    pass
