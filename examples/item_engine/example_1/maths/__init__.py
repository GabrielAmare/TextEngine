from item_engine.textbase.elements import Char
from item_engine.textbase.elements import Token
from .lexer import lexer
from item_engine.textbase.elements import Token
from item_engine.textbase.elements import Lemma
from .parser import parser
from typing import Iterator
from item_engine import *


__all__ = ['gen_networks']


def gen_networks(lexer_cfg: dict, parser_cfg: dict) -> Iterator[Network]:
    yield Network(function=lexer, input_cls=Char, output_cls=Token, to_ignore=['WHITESPACE'], **lexer_cfg)
    yield ReflexiveNetwork(function=parser, input_cls=Token, output_cls=Lemma, to_ignore=[], **parser_cfg)
