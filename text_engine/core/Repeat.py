from ..base import Rule_Unit, Result_List
from .Parser import Parser


class Repeat(Rule_Unit):
    def parse(self, tokens: list, position: int, parser: Parser, backward: bool = False):
        results = RepeatResult(rule=self, at_position=position)

        while True:
            r_position = results.at_position if backward else results.to_position
            result = self.rule.parse(tokens, r_position, parser, backward)

            if not result:
                results.error = result
                break

            results.append(result, backward)

        return results


class RepeatResult(Result_List):
    error = None

    def __str__(self):
        s = super().__str__() + self.__str_body__()

        if self.error is not None:
            s += "[\n" + \
                 "\n".join(f"  {line}" for line in str(self.error).split("\n")) + \
                 "\n]"
        return s
