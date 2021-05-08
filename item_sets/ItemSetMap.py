from __future__ import annotations
from typing import TypeVar, Dict, List, Generic, FrozenSet, Tuple, Optional, Type, Set

from .ItemSetGlobal import ItemSetGlobal
from .ItemSetLocal import ItemSetLocal

from .functions import comb

__all__ = ["ItemSetMap"]

K = TypeVar("K")
V = TypeVar("V")


class ItemSetMap(Dict[ItemSetGlobal[K], ItemSetLocal[V]], Generic[K, V]):
    def include(self, k: ItemSetGlobal[K], v: ItemSetLocal[V]) -> None:
        if k in self:
            self[k] |= v
        else:
            self[k] = v

    def __call__(self, item: K) -> ItemSetLocal[V]:
        """Given an item, return a local item set of all corresponding values"""
        return ItemSetLocal.union(value for key, value in self.items() if item in key)

    @property
    def alphabet(self) -> List[K]:
        return sorted(frozenset(k for isg_k in self.keys() for k in isg_k.items))

    @property
    def partitioned(self) -> ItemSetMap[K, V]:
        alphabet: List[K] = self.alphabet

        reverted: Dict[ItemSetLocal[V], Set[K]] = {}
        for item in alphabet + [None]:
            islv = self(item)
            if islv in reverted:
                reverted[islv].add(item)
            else:
                reverted[islv] = {item}

        input_cls = list(self.keys())[0].__class__

        result: ItemSetMap[K, V] = ItemSetMap()
        for islv, items in reverted.items():
            if None in items:
                items = frozenset(filter(items.__contains__, alphabet))
                inverted = True
            else:
                items = frozenset(items)
                inverted = False
            isgk = input_cls(items=items, inverted=inverted)
            result[isgk] = islv

        return result
