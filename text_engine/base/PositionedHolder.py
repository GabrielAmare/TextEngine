from .PositionedItem import PositionedItem
from typing import List


class PositionedHolder(PositionedItem):
    items: List[PositionedItem]

    def __init__(self, at_position: int, to_position: int):
        super().__init__(at_position, to_position)
        self.items_at_position = {}
        self.items_to_position = {}

    def append(self, item: PositionedItem):
        self.items_at_position.setdefault(item.at_position, [])
        self.items_at_position[item.at_position].append(item)

        self.items_to_position.setdefault(item.to_position, [])
        self.items_to_position[item.to_position].append(item)

    def extend(self, items):
        for item in items:
            self.append(item)
