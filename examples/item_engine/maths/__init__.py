from typing import Iterator
from item_engine import *
from .lexer import lexer
from .parser import parser

__all__ = ['gen_networks']


def gen_networks(lexer_cfg: dict, parser_cfg: dict) -> Iterator[Network]:
    yield Network(function=lexer, **lexer_cfg)
    yield ReflexiveNetwork(function=parser, **parser_cfg)
