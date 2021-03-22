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

    def _make_tokens(self, text, index: int = 0):
        tokens = []
        try:
            for token in self.lexer.tokenize(text, index, 0):
                tokens.append(token)
        except TokenizeError as e:
            raise EngineTokenizeError(tokens, e)

        return tokens

    def _make_results(self, tokens, identifier: str = Identified.ALL, backward=False, full=True):
        start_position = len(tokens) if backward else 0
        length = len(tokens)
        for result in self.parser.parse(tokens, start_position, identifier, backward):
            if result and (result.at_position == 0 and result.to_position == length or not full):
                yield result

    def _make_contexts(self, results):
        for result in results:
            context = Context()
            try:
                result.build(context)
                yield context
            except BuildResultError:
                pass

    def results(self, text: str, identifier: str = Identified.ALL, index: int = 0, backward=False, full=True):
        tokens = self._make_tokens(text, index)
        results = self._make_results(tokens, identifier, backward, full)
        return results

    def result(self, text: str, identifier: str = Identified.ALL, index: int = 0, backward=False):
        for result in self.results(text, identifier, index, backward):
            return result

    def read(self, text: str, identifier: str = Identified.ALL, index: int = 0, backward=False):
        tokens = self._make_tokens(text, index)
        results = self._make_results(tokens, identifier, backward)
        contexts = self._make_contexts(results)
        for context in contexts:
            ast = context.pile[-1]

            if ast:
                if self.astb is None:
                    return ast
                else:
                    return self.astb(ast)
            else:
                raise InvalidASTError
