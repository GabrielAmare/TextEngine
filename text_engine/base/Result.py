from .PositionedItem import PositionedItem
from .LayeredItem import LayeredItem
from .Rule import Rule
from .Context import Context


class Result(PositionedItem, LayeredItem):
    rule: Rule

    def __init__(self, rule: Rule, at_position: int, to_position: int, layer: int = 0):
        PositionedItem.__init__(self, at_position, to_position)
        LayeredItem.__init__(self, layer)
        self.rule = rule

    def __str__(self):
        return f"<{self.at_position}:{self.to_position}>[{self.layer}]{self.__class__.__name__}"

    def build(self, context: Context):
        raise NotImplementedError
