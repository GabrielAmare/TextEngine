from .PositionedItem import PositionedItem
from .Rule import Rule
from .Context import Context


class Result(PositionedItem):
    rule: Rule

    def __init__(self, rule: Rule, at_position: int, to_position: int):
        PositionedItem.__init__(self, at_position, to_position)
        self.rule = rule

    def __str__(self):
        return f"<{self.at_position}:{self.to_position}>{self.__class__.__name__}"

    def build(self, context: Context):
        raise NotImplementedError
