from ...core import *
from .Optimized_Token import Optimized_Token


class Optimized_Pattern(Pattern):
    def make_token(self, content, at_index, at_position):
        if self.value is None:
            value = content
        elif hasattr(self.value, "__call__"):
            value = self.value(content)
        else:
            value = self.value

        return Optimized_Token(
            pattern_id=id(self),
            content=content,
            at_index=at_index,
            at_position=at_position,
            value=value
        )
