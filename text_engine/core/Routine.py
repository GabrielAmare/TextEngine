from ..base import Result_Unit, Rule_Main, Context, Result_Error
from .Parser import Parser


class Routine(Rule_Main):
    def parse(self, tokens: list, position: int, parser: Parser, backward: bool = False):
        result = self.rule.parse(tokens, position, parser, backward)
        if result:
            return RoutineResult(rule=self, result=result)
        else:
            return Result_Error(
                rule=self,
                at_position=position,
                reason=f"Failed to build {repr(self.identifier)} at {position}",
                result=result
            )


class RoutineResult(Result_Unit):
    rule: Routine

    def __str__(self):
        return super().__str__() + "(" + self.rule.name + ")" + self.__str_body__()

    def build(self, context: Context):
        super().build(context)
