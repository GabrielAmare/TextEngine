from examples.item_engine.example_1.define import engine

engine.build(allow_overwrite=True)

from examples.item_engine.example_1.maths.lexer import lexer
from examples.item_engine.example_1.maths.parser import parser
from examples.item_engine.example_1.maths.materials import build

from item_engine.textbase import make_characters

from tools37 import ReprTable


def rt_tokens(tokens) -> ReprTable:
    return ReprTable.from_items(tokens, {
        "at": lambda token: repr(token.at),
        "to": lambda token: repr(token.to),
        "type": lambda token: token.value,
        "content": lambda token: repr(token.content)
    })


def rt_lemmas(tokens) -> ReprTable:
    return ReprTable.from_items(tokens, {
        "at": lambda lemma: repr(lemma.at),
        "to": lambda lemma: repr(lemma.to),
        "type": lambda lemma: str(lemma.value),
        "childs": lambda lemma: "\n".join(f"{key!r}: {val!r}" for key, val in lemma.data.items())
    })


def show_tokens(tokens):
    print(str(rt_tokens(tokens)))


def best_guesses(lemmas):
    to = 0
    guesses = []
    for lemma in lemmas:
        if lemma.value == 'EOF':
            if guesses and guesses[0].to != lemma.at:
                guesses = []
            break

        if lemma.at == 0:
            if lemma.to > to:
                guesses = [lemma]
                to = lemma.to
            elif lemma.to == to:
                guesses.append(lemma)

    return guesses


from time import time


def get_tokens(text: str):
    return list(lexer(make_characters(text, eof=True)))


def get_lemmas(text: str):
    return list(parser(lexer(make_characters(text, eof=True))))


def get_builds(text: str):
    return list(map(build, run(text)))


def run(text: str):
    ti = time()
    lemmas = best_guesses(parser(lexer(make_characters(text, eof=True))))
    tf = time()
    print(f"it took {(tf - ti) * 1e6 / len(text)}µs/char (total of {int((tf - ti) * 1e6)} µs)")
    return lemmas


def main():
    while True:
        text = input("formule :")

        if not text:
            break

        # print(str(rt_lemmas(parser(lexer(make_characters(text, eof=True))))))

        try:
            for obj in get_builds(text):
                print(repr(obj))
        except SyntaxError:
            print("syntax error !")


if __name__ == '__main__':
    main()
