from typing import Iterator
from item_engine import *
from item_engine.textbase.elements import Char, Token
from .lexer import lexer


__all__ = ['gen_networks']


def gen_networks(lexer_cfg: dict) -> Iterator[Network]:
    yield Network(function=lexer, input_cls=Char, output_cls=Token, to_ignore=['WHITESPACE'], **lexer_cfg)
