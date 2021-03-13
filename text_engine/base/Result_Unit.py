from .Result import Result
from .Rule import Rule
from .Context import Context


class Result_Unit(Result):
    result: Result

    def __init__(self, rule: Rule, result: Result):
        Result.__init__(self, rule, result.at_position, result.to_position, result.layer + 1)
        self.result = result

    def __str_body__(self):
        body = "\n".join(f"  {line}" for line in str(self.result).split("\n"))
        return "[\n" + body + "\n]" if body else "[]"

    def __bool__(self):
        return bool(self.result)

    def build(self, context: Context):
        self.result.build(context)
