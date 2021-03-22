from .PositionedItem import PositionedItem
from typing import List


class PositionedPart(PositionedItem):
    items: List[PositionedItem]

    def __init__(self, at_position: int, to_position: int):
        super().__init__(at_position, to_position)
        self.items = []
        self.items_at_position = {}
        self.items_to_position = {}

    def _add(self, item: PositionedItem):
        self.items_at_position.setdefault(item.at_position, [])
        self.items_at_position[item.at_position].append(item)

        self.items_to_position.setdefault(item.to_position, [])
        self.items_to_position[item.to_position].append(item)

    def add_right(self, item: PositionedItem):
        assert self.to_position == item.at_position
        self.items.append(item)
        self.to_position = item.to_position
        self._add(item)

    def add_left(self, item: PositionedItem):
        assert self.at_position == item.to_position
        self.items.insert(0, item)
        self.at_position = item.at_position
        self._add(item)

