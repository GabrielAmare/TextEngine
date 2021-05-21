from item_engine.textbase.elements import Char, Token
from typing import Iterator


def function(src: Iterator[Char]) -> Iterator[Token]:
    cur: Token = Token(at=0, to=0, value=0)
    for old in src:
        while cur.to == old.at:
            new: Token = cur.develop(_function(cur, old), old)
            if not new.is_terminal:
                cur = new
                continue
            if new.is_valid:
                cur = Token(at=new.to, to=new.to, value=0)
                yield new
                continue
            if old.value == 'EOF':
                yield Token.EOF(old.to)
                break
            raise SyntaxError((cur, old, new))
