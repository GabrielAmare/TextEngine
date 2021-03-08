from ..base import PositionedItem, IndexedItem


class Token(PositionedItem, IndexedItem):
    content: str

    def __init__(self, pattern, content: str, at_index: int, at_position: int, value=None):
        PositionedItem.__init__(self, at_position, at_position + 1)
        IndexedItem.__init__(self, at_index, at_index + len(content))

        self.pattern = pattern
        self.content = content
        self.value = value

    def __str__(self):
        return f"[{self.at_index}: {self.to_index}]".ljust(10) + " | " + self.pattern.name.ljust(10) + " | " + repr(self.value).ljust(10)
