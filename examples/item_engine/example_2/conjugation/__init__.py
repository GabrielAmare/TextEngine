from typing import Iterator
from item_engine import *
from .mood_lexer import mood_lexer

__all__ = ['gen_networks']


def gen_networks(mood_lexer_cfg: dict) -> Iterator[Network]:
    yield Network(function=mood_lexer, **mood_lexer_cfg)
