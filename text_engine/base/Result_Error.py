from .Result import Result
from .Rule import Rule
from .Context import Context


class Result_Error(Result):
    def __init__(self, rule: Rule, at_position: int, reason="", result=None):
        to_position = at_position if result is None else result.to_position
        layer = 0 if result is None else result.layer + 1
        super().__init__(rule, at_position, to_position, layer)
        self.reason = reason
        self.result = result

    def __str__(self):
        s = super().__str__() + "(" + repr(self.reason) + ")"

        if self.result is not None:
            s += "[\n" + \
                 "\n".join(f"  {line}" for line in str(self.result).split("\n")) + \
                 "\n]"

        return s

    def __bool__(self):
        return False

    def build(self, context: Context):
        pass
