from ..base import Rule_Unit, Rule, Result_Unit, Context, Result_Error


class In(Rule_Unit):
    key: str

    def __init__(self, key: str, rule: Rule):
        self.key = key
        Rule_Unit.__init__(self, rule)

    def __str__(self):
        return self.__class__.__name__ + "(" + self.key + ")" + "[\n" + \
               "\n".join(f"  {line}" for line in str(self.rule).split("\n")) + \
               "\n]"

    def parse(self, tokens: list, position: int, parser, backward: bool = False):
        result = self.rule.parse(tokens, position, parser, backward)
        if result:
            return InResult(rule=self, result=result)
        else:
            return Result_Error(
                rule=self,
                at_position=position,
                reason="",
                result=result
            )


class InResult(Result_Unit):
    rule: In

    def __str__(self):
        return super().__str__() + "(" + self.rule.key + ")" + self.__str_body__()

    def build(self, context: Context):
        super().build(context)
        context.key_add(self.rule.key, context.pop_last())
