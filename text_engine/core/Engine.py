from .Lexer import Lexer, TokenizeError
from .Parser import Parser
from .ASTB import ASTB
from ..base import Identified, Context


class BuildResultError(Exception):
    pass


class InvalidASTError(Exception):
    pass


class Engine:
    lexer: Lexer
    parser: Parser
    astb: ASTB

    def __init__(self, lexer: Lexer, parser: Parser, astb: ASTB = None):
        self.lexer = lexer
        self.parser = parser
        self.astb = astb

    def read(self, text: str, identifier: str = Identified.ALL, index: int = 0):

        try:
            tokens = self.lexer.tokenize(text, index, 0)
        except TokenizeError as e:
            raise e

        for result in self.parser.parse(tokens, 0, identifier):
            context = Context()

            try:
                result.build(context)
            except BuildResultError as e:
                raise e

            ast = context.pile[-1]

            if ast:
                if self.astb is None:
                    return ast
                else:
                    return self.astb(ast)
            else:
                raise InvalidASTError
