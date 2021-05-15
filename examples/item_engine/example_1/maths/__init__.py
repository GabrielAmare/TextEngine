from typing import Iterator
from item_engine import *
from item_engine.textbase.elements import Char, Token, Lemma
from .lexer import lexer
from .parser import parser


__all__ = ['gen_networks']


def gen_networks(lexer_cfg: dict, parser_cfg: dict) -> Iterator[Network]:
    yield Network(function=lexer, input_cls=Char, output_cls=Token, to_ignore=['WHITESPACE'], **lexer_cfg)
    yield ReflexiveNetwork(function=parser, input_cls=Token, output_cls=Lemma, to_ignore=[], **parser_cfg)
