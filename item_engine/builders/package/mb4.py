from item_engine.textbase.elements import Char, Token
from typing import Dict, Iterator, List


def function(src: Iterator[Char]) -> Iterator[Token]:
    curs: Dict[int, List[Token]] = {}
    def add_cur(cur: Token):
        to = cur.to
        if to not in curs:
            curs[to] = [cur]
        elif cur not in curs[to]:
            curs[to].append(cur)
    
    add_cur(Token(at=0, to=0, value=0))
    for old in src:
        queue = curs.get(old.at, [])
        i = 0
        while i < len(queue):
            cur: Token = queue[i]
            i += 1
            for new in (cur.develop(res, old) for res in _function(cur, old)):
                if not new.is_terminal:
                    add_cur(new)
                    continue
                if new.is_valid:
                    add_cur(Token(at=new.to, to=new.to, value=0))
                    yield new
                    continue
        if old.value == 'EOF':
            yield Token.EOF(old.to)
            break
