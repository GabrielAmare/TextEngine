from .Rule import Rule


class Rule_Unit(Rule):
    rule: Rule

    def __init__(self, rule: Rule):
        self.rule = rule

    def __str__(self):
        return self.__class__.__name__ + "[\n" + \
               "\n".join(f"  {line}" for line in str(self.rule).split("\n")) + \
               "\n]"

    def parse(self, tokens: list, position: int, parser, backward: bool = False):
        raise NotImplementedError
