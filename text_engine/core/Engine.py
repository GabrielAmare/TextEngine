from .Lexer import Lexer, TokenizeError
from .Parser import Parser
from .ASTB import ASTB
from ..base import Identified, Context


class BuildResultError(Exception):
    pass


class InvalidASTError(Exception):
    pass


class EngineTokenizeError(Exception):
    def __init__(self, tokens, tokenize_error=None):
        self.tokens = tokens
        self.tokenize_error = tokenize_error

    def __str__(self):
        return "\n".join(
            f"{token.pattern.name.ljust(10)} | {repr(token.content)}"
            for token in self.tokens
        ) + ("\n\n" + str(self.tokenize_error) if self.tokenize_error else "")


class Engine:
    lexer: Lexer
    parser: Parser
    astb: ASTB

    def __init__(self, lexer: Lexer, parser: Parser, astb: ASTB = None):
        self.lexer = lexer
        self.parser = parser
        self.astb = astb

    def read(self, text: str, identifier: str = Identified.ALL, index: int = 0, backward=False):

        tokens = []
        try:
            for token in self.lexer.tokenize(text, index, 0):
                tokens.append(token)
        except TokenizeError as e:
            raise EngineTokenizeError(tokens, e)

        start_position = len(tokens) if backward else 0

        for result in self.parser.parse(tokens, start_position, identifier, backward):
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
