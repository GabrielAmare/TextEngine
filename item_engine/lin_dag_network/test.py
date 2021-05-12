from typing import Tuple

from item_engine.constants import *

from item_engine.lin_lin_network import Model as LL_Model

from item_engine.lin_dag_network import Model as LD_Model

from item_engine.textbase import make_characters, Char, Token, Lemma

if __name__ == '__main__':

    calls_to = {}


    def memorize(function):
        cache = {}

        def wrapper(value, element):
            key = (value, element.value)
            global calls_to
            calls_to.setdefault(key, 0)
            calls_to[key] += 1
            if key in cache:
                return cache[key]
            else:
                cache[key] = result = function(value, element)
                return result

        return wrapper


    letters = 'abcdefghijklmnopqrstuvwxyz' + 'é'


    @memorize
    def function_lexer(token: Token, char: Char) -> Tuple[ACTION, STATE]:
        if token.value == 0:
            if char.value == ' ':
                return INCLUDE, 'SPACE'
            elif char.value == ',':
                return INCLUDE, 'COMMA'
            elif char.value in letters:
                return INCLUDE, 1
        elif token.value == 1:
            if char.value in letters:
                return INCLUDE, 1
            else:
                return EXCLUDE, token.content
        else:
            raise ValueError(f"invalid value : {token.value!r}")


    def function_parser1(lemma: Lemma, token: Token) -> Tuple[Tuple[ACTION, STATE], ...]:
        if lemma.value == 0:
            if token.value in ('je',):
                return (AS.format('word'), "PRO-PER"),
            elif token.value in ('mangerais',):
                return (AS.format('word'), "VER-CON"),
            elif token.value in ('le', 'la', 'l', 'les'):
                return (AS.format('word'), "ART-DEF"),
            elif token.value in ('viande', 'légumes'):
                return (AS.format('word'), "NOM-COM"),
            elif token.value in ('ne',):
                return (AS.format('word'), "NEG-L"),
            elif token.value in ('pas',):
                return (AS.format('word'), "NEG-R"),
            else:
                return (AS.format('word'), "?"),
        else:
            raise ValueError(f"invalid value : {lemma.value!r}")


    def function_parser2(lemma: Lemma, token: Lemma) -> Tuple[Tuple[ACTION, STATE], ...]:
        if lemma.value == 0:
            if token.value in ('ART-DEF', 'ART-IND'):
                return ("as:article", 1),
            if token.value == "NEG-L":
                return (INCLUDE, 2),
            elif token.value == "EOF":
                return (EXCLUDE, "!"),
            else:
                return ("as:copy", token.value),
        elif lemma.value == 1:
            if token.value == 'NOM-COM':
                return ("as:noun", 'GRP-NOM'),
            else:
                return (EXCLUDE, "!GRP-NOM"),
        elif lemma.value == 2:
            if token.value == "VER-CON":
                return ("as:verb", 3),
            else:
                return (EXCLUDE, "!VER-CON-NEG"),
        elif lemma.value == 3:
            if token.value == "NEG-R":
                return (INCLUDE, "VER-CON-NEG"),
            else:
                return (EXCLUDE, "!VER-CON-NEG"),

        else:
            raise ValueError(f"invalid value : {lemma.value!r}")


    def function_parser3(lemma: Lemma, token: Lemma) -> Tuple[Tuple[ACTION, STATE], ...]:
        if lemma.value == 0:
            if token.value == "PRO-PER":
                return ("as:pronoun", 1),
            else:
                return (EXCLUDE, "!"),
        elif lemma.value == 1:
            if token.value == 'VER-CON':
                return ("as:verb", 2),
            elif token.value == 'VER-CON-NEG':
                return ("as:verb", 3),
            else:
                return (EXCLUDE, "!GRP-VER|GRP-VER-NEG"),
        elif lemma.value == 2:
            if token.value == 'GRP-NOM':
                return ("as:grp-nom", "GRP-VER"),
            else:
                return (EXCLUDE, "!GRP-VER"),
        elif lemma.value == 3:
            if token.value == 'GRP-NOM':
                return ("as:grp-nom", "GRP-VER-NEG"),
            else:
                return (EXCLUDE, "!GRP-VER-NEG"),
        else:
            raise ValueError(f"invalid value : {lemma.value!r}")

    from tools37 import ReprTable


    lexer = LL_Model(input_cls=Char, output_cls=Token, function=function_lexer, skips=["SPACE"])
    parser1 = LD_Model(input_cls=Token, output_cls=Lemma, function=function_parser1, skips=[], allow_gaps=True)
    parser2 = LD_Model(input_cls=Lemma, output_cls=Lemma, function=function_parser2, skips=[], allow_gaps=True)
    parser3 = LD_Model(input_cls=Lemma, output_cls=Lemma, function=function_parser3, skips=[], allow_gaps=True)

    text = "je mangerais les légumes mais je ne mangerais pas la viande"

    characters = make_characters(text)

    tokens = lexer.generate(characters)

    print(ReprTable.from_items(
        tokens,
        dict(
            span=lambda token: f"{token.start} → {token.end}",
            type=lambda token: token.value,
            content=lambda token: repr(token.content)
        )
    ))

    lemmas1 = parser1.generate(tokens)

    print(ReprTable.from_items(
        lemmas1,
        dict(
            span=lambda lemma: f"{lemma.start} → {lemma.end}",
            type=lambda lemma: lemma.value,
            data=lambda lemma: "\n".join(f"{k}: {v!r}" for k, v in lemma.data.items())
        )
    ))

    lemmas2 = parser2.generate(lemmas1)

    print(ReprTable.from_items(
        lemmas2,
        dict(
            span=lambda lemma: f"{lemma.start} → {lemma.end}",
            type=lambda lemma: lemma.value,
            data=lambda lemma: "\n".join(f"{k}: {v!r}" for k, v in lemma.data.items())
        )
    ))

    lemmas3 = parser3.generate(lemmas2)

    print(ReprTable.from_items(
        lemmas3,
        dict(
            span=lambda lemma: f"{lemma.start} → {lemma.end}",
            type=lambda lemma: lemma.value,
            data=lambda lemma: "\n".join(f"{k}: {v!r}" for k, v in lemma.data.items())
        )
    ))
