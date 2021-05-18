import unittest
from typing import Tuple
from item_engine.textbase import *


def compare(old: str, new: str) -> Tuple[str, str]:
    with open(old, mode="r", encoding="utf-8") as file:
        old_content = file.read()

    with open(new, mode="r", encoding="utf-8") as file:
        new_content = file.read()

    return old_content, new_content


class TestStack(unittest.TestCase):
    """
        Each test method here will re-generate a parsing module to insure file equality
    """

    def test_001(self):
        lexer, kws, sym = MakeLexer(
            keywords=[
                ' and ', ' or ', 'not '
            ],
            symbols=[
                ' = ', ' + ', ' - ', ' / ', ' * ', ' ** ',  # operations
                ' == ', ' < ', ' <= ', ' > ', ' >= ',  # comparisons
                '( ', ' )',  # parenthesis
                '{ ', ' }',  # splines
                '[ ', ' ]',  # brackets
                '\n', ', ',  # separators
                ' | ', ' & ', '!'  # binary symbols
            ],
            branches=dict(
                WHITESPACE=charset(" \t").inc().repeat(1, INF),
                ID=alpha & alphanum.repeat(0, INF),
                INT=digits.repeat(1, INF),
                FLOAT=digits.repeat(1, INF) & dot & digits.repeat(0, INF) | dot & digits.repeat(1, INF),
            )
        )

        engine = Engine(
            name="new",
            parsers=[
                Parser(
                    name='lexer',
                    branch_set=lexer,
                    input_cls=Char,
                    output_cls=Token,
                    skips=["WHITESPACE"],
                    reflexive=False,
                    formal=True,
                ),
            ]
        )

        engine.build(root="test_001", allow_overwrite=True)

        self.assertEqual(
            *compare(
                "test_001/old/lexer.py",
                "test_001/new/lexer.py"
            )
        )
        #
        # from tests.test_001.new import gen_networks
        #
        # characters = make_characters(text="", eof=True)
        #
        # network, = gen_networks(
        #     lexer_cfg=dict(
        #         allow_gaps=True,
        #         save_terminals=True,
        #         remove_previous=False
        #     )
        # )

    def test_INT(self):
        lexer, kws, sym = MakeLexer(branches=dict(INT=digits.repeat(1, INF)))

        engine = Engine(
            name="new",
            parsers=[
                Parser(
                    name='lexer',
                    branch_set=lexer,
                    input_cls=Char,
                    output_cls=Token,
                    skips=[],
                    reflexive=False,
                    formal=True,
                ),
            ]
        )

        engine.build(root="test_002", allow_overwrite=True)

        self.assertEqual(
            *compare(
                "test_002/old/lexer.py",
                "test_002/new/lexer.py"
            )
        )
        from tests.test_002.new import gen_networks

        network, = gen_networks()

        #
        # from tests.test_001.new import gen_networks
        #
        # characters = make_characters(text="", eof=True)
        #
        # network, = gen_networks(
        #     lexer_cfg=dict(
        #         allow_gaps=True,
        #         save_terminals=True,
        #         remove_previous=False
        #     )
        # )


if __name__ == '__main__':
    unittest.main()
