from functools import reduce
from operator import and_, or_
from typing import *

INPUT = TypeVar("INPUT")
OUTPUT = TypeVar("OUTPUT")

K = TypeVar("K")
V = TypeVar("V")


class ItemSet(Generic[K]):
    def __contains__(self, item: K) -> bool:
        """Return True if the ItemSet contains the given item"""
        raise NotImplementedError

    def __eq__(self, other):
        """Return the union of two ItemSets"""
        raise NotImplementedError

    def __or__(self, other):
        """Return the union of two ItemSets"""
        raise NotImplementedError

    def __and__(self, other):
        """Return the intersection of two ItemSets"""
        raise NotImplementedError

    def __ior__(self, other):
        """Return the union of two ItemSets"""
        return self | other

    def __iand__(self, other):
        """Return the intersection of two ItemSets"""
        return self & other

    def __invert__(self):
        """Return the inversion of the ItemSet"""
        raise NotImplementedError

    def __hash__(self):
        """Return the hash of the ItemSet"""
        raise NotImplementedError

    @classmethod
    def intersection(cls, items):
        if items:
            return reduce(and_, items)
        else:
            return cls.always()

    @classmethod
    def union(cls, items):
        if items:
            return reduce(or_, items)
        else:
            return cls.never()

    @classmethod
    def never(cls):
        raise NotImplementedError

    @classmethod
    def always(cls):
        raise NotImplementedError

    @property
    def is_never(self) -> bool:
        """Return True is the ItemSet correspond to a never matching set"""
        raise NotImplementedError

    @property
    def is_always(self) -> bool:
        """Return True is the ItemSet correspond to an always matching set"""
        raise NotImplementedError


def comb(n: int) -> Generator[Generator[bool, None, None], None, None]:
    for k in range(2 ** n):
        yield (bool(k & 2 ** i) for i in range(n - 1, -1, -1))


def dict_or(d: Dict[K, V], k: K, v: V) -> None:
    if k in d:
        d[k] |= v
    else:
        d[k] = v


def juxt(operations: Dict[ItemSet[INPUT], ItemSet[OUTPUT]]) -> Dict[ItemSet[INPUT], ItemSet[OUTPUT]]:
    """
        for two keys k1 & k2 in ``operations``
        it is possible that (e in k1 and e in k2) == True

        this function return a new Dict[ItemSet[INPUT], ItemSet[OUTPUT]] such as :
        for two keys k1 & k2 in the new dict
        it's never possible that (e in k1 and e in k2) == True

        Transform a list of operations into another list of operations
        the new list will have the following property :
            if we have an input i: INPUT,
            it will be contained by 1 and always 1 of the result operations

        strong supposition : there will always be an empty ItemSet either in the keys or in the values

        strong supposition :
            considering :
                x : True if an empty set is present in the keys
                y : True if an empty set is present in the values

                hypothesis : !x => y
                    if there's no empty set in the keys, there WILL be an empty set in the values

                an empty set in the keys means that there's no unhandled case
                an empty set in the values means that there's a case where

        if there is N operations, the time complexity will be O(N * 2^N)
    """
    result: Dict[ItemSet[INPUT], ItemSet[OUTPUT]] = {}

    input_cls = list(operations.keys())[0].__class__
    output_cls = list(operations.values())[0].__class__

    for sign in comb(len(operations)):  # O(2 ** len(operations))
        case_inputs: List[ItemSet[INPUT]] = []
        case_outputs: List[ItemSet[OUTPUT]] = []
        for b, op_inputs, op_outputs in zip(sign, *zip(*operations.items())):  # O(len(operations))
            if b:
                case_inputs.append(op_inputs)
                case_outputs.append(op_outputs)
            else:
                case_inputs.append(~op_inputs)

        dict_or(
            d=result,
            k=input_cls.intersection(case_inputs),
            v=output_cls.union(case_outputs)
        )

    assert any((k1 & k2).is_never for k1 in result.keys() for k2 in result.keys() if k1 is not k2)
    assert any(k.is_never for k in result.keys()) or any(v.is_never for v in result.values())

    return result


def merge(operations: Dict[ItemSet[INPUT], ItemSet[OUTPUT]]) -> Dict[ItemSet[INPUT], ItemSet[OUTPUT]]:
    rmap: Dict[ItemSet[OUTPUT], ItemSet[INPUT]] = {}

    for k, v in juxt(operations).items():
        if v in rmap:
            rmap[v] |= k
        else:
            rmap[v] = k

    result: Dict[ItemSet[INPUT], ItemSet[OUTPUT]] = {v: k for k, v in rmap.items()}

    assert len(result.keys()) < 2 or \
           any((k1 & k2).is_never for k1 in result.keys() for k2 in result.keys() if k1 is not k2)

    # if the hypothesis is valid, this should never raise
    # HYPOTHESIS : if there's a 'never' set in the keys,
    #              it's not possible an 'always' set is in the keys
    #              and a 'never' set is in the values
    #              and an 'always' set is in the values
    if not any(k.is_never for k in result.keys()):
        assert not (
                any(k.is_always for k in result.keys()) and
                any(v.is_never for v in result.values()) and
                any(v.is_always for v in result.values())
        )

    # there cannot exist an item which belongs to two different keys
    # there can't be two equal keys
    # there can't be two equal values either
    # there can still exist items which belongs to two different values

    return result


def string_difference(s1: str, s2: str) -> str:
    return ''.join(c for c in s1 if c not in s2)


class CharSet(ItemSet[str]):
    def __init__(self, expr: str, inverted: bool = False):
        self.expr: str = ''.join(sorted(set(expr)))
        self.inverted: bool = inverted

    def __bool__(self):
        """Return True if the charset contains any char"""
        return self.expr != '' or self.inverted

    def __repr__(self):
        if self.expr == '':
            if self.inverted:
                return 'always'
            else:
                return 'never'
        return ('~' if self.inverted else '') + repr(self.expr)

    def __contains__(self, c: str) -> bool:
        if self.inverted:
            return c not in self.expr
        else:
            return c in self.expr

    def __eq__(self, other):
        return type(self) is type(other) and self.expr == other.expr and self.inverted == other.inverted

    def __or__(self, other):
        assert isinstance(other, CharSet)
        return ~(~self & ~other)

    def __and__(self, other):
        if self.inverted:
            if other.inverted:
                return CharSet(self.expr + other.expr, True)
            else:
                return CharSet(string_difference(other.expr, self.expr), False)
        else:
            if other.inverted:
                return CharSet(string_difference(self.expr, other.expr), False)
            else:
                return CharSet(''.join(c for c in self.expr + other.expr if c in self and c in other), False)

    def __invert__(self):
        return CharSet(self.expr, not self.inverted)

    def __hash__(self):
        return hash((type(self), self.expr))

    @classmethod
    def never(cls):
        return cls('', False)

    @classmethod
    def always(cls):
        return cls('', True)

    @property
    def is_never(self) -> bool:
        """Return True is the ItemSet correspond to a never matching set"""
        return self.expr == '' and not self.inverted

    @property
    def is_always(self) -> bool:
        """Return True is the ItemSet correspond to an always matching set"""
        return self.expr == '' and self.inverted


data = []

keys = [
    CharSet.never(), CharSet.always(),
    CharSet('A'), ~CharSet('A'),
    CharSet('B'), ~CharSet('B'),
    CharSet('AB'), ~CharSet('AB')
]
vals = [
    CharSet.never(), CharSet.always(),
    CharSet('X'), CharSet('X', True),
    CharSet('Y'), CharSet('Y', True),
    CharSet('XY'), CharSet('XY', True)
]

for k1 in keys:
    for v1 in vals:
        for k2 in keys:
            for v2 in vals:
                # for k3 in keys:
                #     for v3 in vals:
                d = {k1: v1, k2: v2}
                data.append((d, merge(d)))

signs: set = set()

for k, v in data:
    # print(k, "->", v)

    never_in_keys = sum(1 for e in v.keys() if e.is_never)
    always_in_keys = sum(1 for e in v.keys() if e.is_always)

    never_in_vals = sum(1 for e in v.values() if e.is_never)
    always_in_vals = sum(1 for e in v.values() if e.is_always)
    s = (never_in_keys, always_in_keys, never_in_vals, always_in_vals)

    assert all(b in (0, 1) for b in s)

    for e1 in v.values():
        for e2 in v.values():
            if e1 is not e2:
                assert e1 != e2

    signs.add(s)


def resume_bin(data: List[Tuple[bool, ...]]):
    n = len(data[0])

    for s in map(tuple, comb(n)):
        yield s, s in data


for s, r in resume_bin(list(signs)):
    print(''.join('01'[b] for b in s), '01'[r])
