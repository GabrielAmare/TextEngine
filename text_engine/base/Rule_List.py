from .Rule import Rule
from typing import List, Iterable


class Rule_List(Rule):
    rules: List[Rule]

    def __init__(self, *rules: Rule):
        self.rules = list(rules)

    def __str__(self):
        return self.__class__.__name__ + "[\n" + \
               "\n".join(f"  {line}" for line in "\n".join(map(str, self.rules)).split("\n")) + \
               "\n]"

    def parse(self, tokens: list, position: int, parser):
        raise NotImplementedError
