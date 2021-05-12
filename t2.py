from typing import *

E = TypeVar("E")
F = TypeVar("F")
G = TypeVar("G")


class Bijection(Generic[E, F]):
    pass


def chain(A: Bijection[E, F], B: Bijection[F, G]) -> Bijection[E, G]:
    raise NotImplementedError
