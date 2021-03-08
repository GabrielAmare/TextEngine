class Rule:
    def parse(self, tokens: list, position: int, parser):
        raise NotImplementedError

    def __and__(self, other):
        raise NotImplementedError

    def __or__(self, other):
        raise NotImplementedError
