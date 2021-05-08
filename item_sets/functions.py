from typing import Generator

__all__ = ["comb"]


def comb(n: int) -> Generator[Generator[bool, None, None], None, None]:
    for k in range(2 ** n):
        yield (bool(k & 2 ** i) for i in range(n - 1, -1, -1))
