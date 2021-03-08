from ..base import Rule_List, Result_List, Result_Error
from .Parser import Parser


class All(Rule_List):
    def parse(self, tokens: list, position: int, parser: Parser):
        results = AllResult(rule=self, at_position=position)

        for rule in self.rules:
            result = rule.parse(tokens, results.to_position, parser)

            if not result:
                results.append(result)
                break

            results.append(result)

        return results


class AllResult(Result_List):
    def __bool__(self):
        return all(map(bool, self.results))

    def __str__(self):
        return super().__str__() + self.__str_body__()
