from ..base import Rule_List, Result_Unit, Result_Error, Result_List
from .Parser import Parser


class Any(Rule_List):
    def parse(self, tokens: list, position: int, parser: Parser, backward: bool = False):
        errors = Result_List(rule=self, at_position=position)
        for rule in self.rules:
            result = rule.parse(tokens, position, parser, backward)
            if result:
                return AnyResult(rule=self, result=result)
            else:
                errors.append(result)

        return Result_Error(
            rule=self,
            at_position=position,
            reason=f"No matching rule in Any",
            result=errors,
        )


class AnyResult(Result_Unit):
    def __str__(self):
        return super().__str__() + self.__str_body__()
