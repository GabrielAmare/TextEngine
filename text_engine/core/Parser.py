from ..base import Identified, Rule_Main
from typing import List


class Parser:
    builders: List[Rule_Main]

    def __init__(self, *builders: Rule_Main):
        self.builders = list(builders)

    def get_all_matching_builders(self, identifier: str):
        for builder in self.builders:
            if builder <= identifier:
                yield builder

    def parse(self, tokens: list, position: int, identifier: str = Identified.ALL, backward: bool = False):
        for builder in self.get_all_matching_builders(identifier):
            result = builder.parse(tokens, position, self, backward)
            yield result

    def add_builder(self, identifier, rule):
        raise NotImplementedError

    def add_routine(self, identifier, rule):
        raise NotImplementedError
