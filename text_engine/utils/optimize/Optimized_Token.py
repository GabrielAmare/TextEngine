from ...base import PositionedItem, LayeredItem, IndexedItem


class Optimized_Token(PositionedItem, LayeredItem, IndexedItem):
    content: str

    def __init__(self, pattern_id, content: str, at_index: int, at_position: int, value=None):
        PositionedItem.__init__(self, at_position, at_position + 1)
        IndexedItem.__init__(self, at_index, at_index + len(content))
        LayeredItem.__init__(self, layer=0)

        self.pattern_id = pattern_id
        self.content = content
        self.value = value
