from .Rule import Rule
from .Rule_Unit import Rule_Unit
from .Identified import Identified


class Rule_Main(Rule_Unit, Identified):
    def __init__(self, identifier: str, rule: Rule):
        Identified.__init__(self, identifier)
        Rule_Unit.__init__(self, rule)

    def __str__(self):
        return self.__class__.__name__ + "(" + self.identifier + ")" + "[\n" + \
               "\n".join(f"  {line}" for line in str(self.rule).split("\n")) + \
               "\n]"

    def parse(self, tokens: list, position: int, parser):
        raise NotImplementedError
