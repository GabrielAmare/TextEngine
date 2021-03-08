from ..base import Rule_List, Result_Unit, Result_Error
from .Parser import Parser


class Any(Rule_List):
    def parse(self, tokens: list, position: int, parser: Parser):
        for rule in self.rules:
            result = rule.parse(tokens, position, parser)
            if result:
                return AnyResult(rule=self, result=result)
            else:
                return Result_Error(
                    rule=self,
                    at_position=position,
                    reason=f"No matching rule in Any",
                    result=result,
                )


class AnyResult(Result_Unit):
    def __str__(self):
        return super().__str__() + self.__str_body__()
