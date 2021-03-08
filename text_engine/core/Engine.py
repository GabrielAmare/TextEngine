from .Lexer import Lexer, TokenizeError
from .Parser import Parser
from ..base import Identified, Context


class BuildResultError(Exception):
    pass


class InvalidASTError(Exception):
    pass


class Engine:
    lexer: Lexer
    parser: Parser

    def __init__(self, lexer: Lexer, parser: Parser):
        self.lexer = lexer
        self.parser = parser

    def read(self, text: str, identifier: str = Identified.ALL, index: int = 0):

        try:
            tokens = self.lexer.tokenize(text, index, 0)
        except TokenizeError as e:
            raise e

        for result in self.parser.parse(tokens, 0, identifier):
            if result and result.at_position == 0 and result.to_position == len(tokens):
                context = Context()

                try:
                    result.build(context)
                except BuildResultError as e:
                    raise e

                ast = context.pile[-1]
                if ast:
                    return ast
                else:
                    raise InvalidASTError
