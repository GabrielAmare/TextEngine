from typing import Iterator

from item_engine import *
from .items import *
from .elements import *

__all__ = ["charset", "string", "match", "non_match", "make_characters", "make_branch_set"]


def charset(s: str) -> CharG:
    return CharG(frozenset(map(CharI, s)))


def string(s: str) -> All:
    return All(tuple(match(charset(c)) for c in s))


def match(cs: CharG) -> Match:
    return cs.match("include")


def non_match(cs: CharG) -> Match:
    return cs.match("ignore")


def make_characters(text: str) -> Iterator[Char]:
    for index, char in enumerate(text):
        yield Char.make(index, char)


def make_branch_set(*branches: Branch) -> BranchSet:
    return BranchSet(frozenset(branches))
