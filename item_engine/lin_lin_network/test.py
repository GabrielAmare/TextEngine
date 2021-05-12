from typing import Tuple

from item_engine.constants import *
from item_engine.lin_lin_network import Model as LL_Model
from item_engine.textbase import make_characters, Char, Token

if __name__ == '__main__':

    calls_to = {}


    def memorize(function):
        cache = {}

        def wrapper(token, char):
            key = (token.value, char.value)
            global calls_to
            calls_to.setdefault(key, 0)
            calls_to[key] += 1
            if key in cache:
                return cache[key]
            else:
                cache[key] = result = function(token, char)
                return result

        return wrapper


    @memorize
    def function(token: Token, char) -> Tuple[ACTION, STATE]:
        """
        parser for :
            VAR = 'abcdefghijklmnopqrstuvwxyz'+
            NUM = '0123456789'+
            VAR_NUM = 'abcdefghijklmnopqrstuvwxyz'+ '0123456789'+
            EQUAL = '='
            PLUS = '+'
            PLUS_EQUAL = '+='
            PLUS_PLUS = '++'
            LP = '('
            RP = ')'
        """
        if token.value == 0:
            if char.value == '=':
                return INCLUDE, 'EQUAL'
            elif char.value == '+':
                return INCLUDE, 7
            elif char.value == '(':
                return INCLUDE, 'LP'
            elif char.value == ')':
                return INCLUDE, 'RP'
            elif char.value == '/':
                return INCLUDE, 'SLASH'
            elif char.value == '-':
                return INCLUDE, 'DASH'
            elif char.value == ' ':
                return INCLUDE, 6
            elif char.value in 'abcefghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif char.value in 'd':
                return INCLUDE, 3
            elif char.value in '0123456789':
                return INCLUDE, 8
            else:
                return EXCLUDE, '!'
        elif token.value == 1:
            if char.value in 'abcdefghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif char.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'VAR'
        elif token.value == 2:
            if char.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'VAR_NUM'
        elif token.value == 3:
            if char.value == 'e':
                return INCLUDE, 4
            elif char.value in 'abcdfghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif char.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'VAR'
        elif token.value == 4:
            if char.value == 'f':
                return INCLUDE, 5
            elif char.value in 'abcdeghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif char.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'VAR'
        elif token.value == 5:
            if char.value in 'abcdefghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif char.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'KW_DEF'
        elif token.value == 6:
            if char.value == ' ':
                return INCLUDE, 6
            else:
                return EXCLUDE, 'SPACE'
        elif token.value == 7:
            if char.value == '+':
                return INCLUDE, 'PLUS_PLUS'
            elif char.value == '=':
                return INCLUDE, 'PLUS_EQUAL'
            else:
                return EXCLUDE, 'PLUS'
        elif token.value == 8:
            if char.value in '0123456789':
                return INCLUDE, 8
            else:
                return EXCLUDE, 'NUM'
        else:
            raise Exception(f"invalid value : {token.value!r}")


    net = LL_Model(
        input_cls=Char,
        output_cls=Token,
        function=function,
        skips=["SPACE"]
    )

    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789+/=() "

    import time
    import random

    size = 10_000
    text = ''.join(random.choice(alphabet) for _ in range(size))
    t = time.time()
    try:
        tokens = net.generate(make_characters(text))
        d = time.time() - t

        print(f"{round((1e6 * d) / len(text))} μs/char [{len(text)} chars]")
        print(f"{round((1e6 * d) / len(tokens))} μs/token [{len(tokens)} tokens]")
        print(f"total time : {round(d, 3)} seconds")
        print()
    except SyntaxError as e:
        print(repr(text))
        print('|' + ''.join('^' if e.args[0].start == index else ' ' for index in range(len(text))) + '|')
        raise e

    len_keys = len(calls_to.keys())
    max_call = max(calls_to.values())
    sum_call = sum(calls_to.values())

    print(f"memorize\n"
          f"number of cases : {len_keys}\n"
          f"maximum calls to a single case : {max_call}\n"
          f"mean calls to a single case : {sum_call / max_call if max_call != 0 else '?'}")

    for key, val in calls_to.items():
        if val >= 0.75 * max_call:
            print(f"{key} occured {val} times")

    text = "abcdef12345 = (x / 120)"

    from tools37 import ReprTable

    print(ReprTable.from_items(items=net.generate(make_characters(text)), config=dict(
        span=lambda token: f"{token.start} → {token.end}",
        type=lambda token: token.value,
        content=lambda token: token.content
    )))
