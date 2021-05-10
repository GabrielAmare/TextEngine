from typing import Tuple

from item_engine.constants import *
from item_engine.linear_formal_network import Model as LFN_Model
from item_engine.textbase import make_characters, Char, Token

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


    @memorize
    def function(value: NT_STATE, element) -> Tuple[ACTION, STATE]:
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
        if value == 0:
            if element.value == '=':
                return INCLUDE, 'EQUAL'
            elif element.value == '+':
                return INCLUDE, 7
            elif element.value == '(':
                return INCLUDE, 'LP'
            elif element.value == ')':
                return INCLUDE, 'RP'
            elif element.value == '/':
                return INCLUDE, 'SLASH'
            elif element.value == '-':
                return INCLUDE, 'DASH'
            elif element.value == ' ':
                return INCLUDE, 6
            elif element.value in 'abcefghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif element.value in 'd':
                return INCLUDE, 3
            elif element.value in '0123456789':
                return INCLUDE, 8
            else:
                return EXCLUDE, '!'
        elif value == 1:
            if element.value in 'abcdefghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif element.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'VAR'
        elif value == 2:
            if element.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'VAR_NUM'
        elif value == 3:
            if element.value == 'e':
                return INCLUDE, 4
            elif element.value in 'abcdfghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif element.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'VAR'
        elif value == 4:
            if element.value == 'f':
                return INCLUDE, 5
            elif element.value in 'abcdeghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif element.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'VAR'
        elif value == 5:
            if element.value in 'abcdefghijklmnopqrstuvwxyz':
                return INCLUDE, 1
            elif element.value in '0123456789':
                return INCLUDE, 2
            else:
                return EXCLUDE, 'KW_DEF'
        elif value == 6:
            if element.value == ' ':
                return INCLUDE, 6
            else:
                return EXCLUDE, 'SPACE'
        elif value == 7:
            if element.value == '+':
                return INCLUDE, 'PLUS_PLUS'
            elif element.value == '=':
                return INCLUDE, 'PLUS_EQUAL'
            else:
                return EXCLUDE, 'PLUS'
        elif value == 8:
            if element.value in '0123456789':
                return INCLUDE, 8
            else:
                return EXCLUDE, 'NUM'
        else:
            raise Exception(f"invalid value : {value!r}")


    net = LFN_Model(
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
        tokens = net.tokenize(make_characters(text))
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

    print(ReprTable.from_items(items=net.tokenize(make_characters(text)), config=dict(
        span=lambda token: f"{token.start} → {token.end}",
        type=lambda token: token.value,
        content=lambda token: token.content
    )))
