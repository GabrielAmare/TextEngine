from typing import List
from .Result import Result
from .Rule import Rule
from .Context import Context


class Result_List(Result):
    results: List[Result]

    def __init__(self, rule: Rule, at_position: int):
        Result.__init__(self, rule, at_position, at_position)
        self.results = []

    def __str_body__(self):
        body = "\n".join(f"  {line}" for line in "\n".join(map(str, self.results)).split("\n"))
        return "[\n" + body + "\n]" if body else "[]"

    def append(self, result: Result):
        assert self.to_position == result.at_position
        self.results.append(result)
        self.to_position = result.to_position

    def build(self, context: Context):
        for result in self.results:
            result.build(context)
