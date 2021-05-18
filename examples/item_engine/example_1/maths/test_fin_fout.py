from examples.item_engine.example_1.maths.lexer import lexer
from item_engine.textbase import Char, Token, make_characters
from typing import Iterator


def tokenize(source: Iterator[Char]):
    current = Token(at=0, to=0, value=0)
    for old in source:
        while current.to == old.at:
            action, value = lexer(current, old)
            new = current.develop(action, value, old)
            if not new.is_terminal:
                current = new
                continue

            if new.is_valid:
                yield new
                current = Token(at=new.to, to=new.to, value=0)
                continue

            if old.value == 'EOF':
                break

            assert new.is_error, "program inconsistency"
            raise SyntaxError((new, old))


def main():
    for token in tokenize(make_characters("12.3456 - x / y - .56 and y ands", eof=True)):
        print(repr(token))


if __name__ == '__main__':
    main()
