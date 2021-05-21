from dataclasses import replace
from item_engine.textbase.elements import Char, Token
from typing import Iterator


def function(src: Iterator[Char]) -> Iterator[Token]:
    cur: Token = Token(at=0, to=0, value=0)
    pos: int = 0
    for old in src:
        while cur.to == old.at:
            new: Token = cur.develop(_function(cur, old), old)
            if not new.is_terminal:
                cur = new
                continue
            if new.is_valid:
                cur = Token(at=new.to, to=new.to, value=0)
                if new.value in ['WHITESPACE']:
                    continue
                else:
                    new = replace(new, at=pos, to=pos + 1)
                    pos += 1
                yield new
                continue
            if old.value == 'EOF':
                yield Token.EOF(old.to)
                break
            raise SyntaxError((cur, old, new))
