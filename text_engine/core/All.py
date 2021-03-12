from ..base import Rule_List, Result_List
from .Parser import Parser


class All(Rule_List):
    def parse(self, tokens: list, position: int, parser: Parser, backward: bool = False):
        rules = reversed(self.rules) if backward else self.rules

        results = AllResult(rule=self, at_position=position)

        for rule in rules:
            r_position = results.at_position if backward else results.to_position
            result = rule.parse(tokens, r_position, parser, backward)

            results.append(result, backward)

            if not result:
                break

        return results


class AllResult(Result_List):
    def __bool__(self):
        return all(map(bool, self.results))

    def __str__(self):
        return super().__str__() + self.__str_body__()
