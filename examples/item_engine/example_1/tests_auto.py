from examples.item_engine.example_1.define import engine

engine.build(allow_overwrite=True)

from examples.item_engine.example_1.maths.lexer import lexer
from examples.item_engine.example_1.maths.parser import parser
from examples.item_engine.example_1.maths.materials import *

from item_engine.textbase import make_characters


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


def get(text: str):
    return list(map(build, best_guesses(parser(lexer(make_characters(text, eof=True))))))


def test(text, expected):
    result = get(text)
    assert expected == result, f"\nexpected: {expected}\nresult: {result}"


test("16x", [Mul(Int(16), Var('x'))])
test("16*x", [Mul(Int(16), Var('x'))])
test("16 * x", [Mul(Int(16), Var('x'))])

test("1+2+3", [Add(Add(Int(1), Int(2)), Int(3))])
test("1*2+3", [Add(Mul(Int(1), Int(2)), Int(3))])
test("1+2*3", [Add(Int(1), Mul(Int(2), Int(3)))])
test("1+2-3", [Sub(Add(Int(1), Int(2)), Int(3))])

test("--x", [Neg(Neg(Var('x')))])
test("1--2", [Sub(Int(1), Neg(Int(2)))])
test("x=2", [Attr(Var('x'), Int(2))])
test("x=y/5", [Attr(Var('x'), Div(Var('y'), Int(5)))])

test("12x-3", [Sub(Mul(Int(12), Var('x')), Int(3))])

# added float
# test("1.", [Float(1.)])
# test(".1", [Float(.1)])
# test("1.1", [Float(1.1)])
# test("253.6", [Float(253.6)])
# test("0.07", [Float(0.07)])

# test(
#     "∀ x ∈ X, ∃ y ∈ Y | x + y == 5 and x * y == 6",
#     [Constraint(
#         ForAll(Var('x'), Var('X')),
#         Exists(Var('y'), Var('Y')),
#         And(Eq(Add(Var('x'), Var('y')), Int(5)), Eq(Mul(Var('x'), Var('y')), Int(6)))
#     )]
# )
