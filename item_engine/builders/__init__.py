"""
    Différentes variantes de constructeurs

    les constructeurs recoivent un flux d'éléments constitutif
    qu'ils agrègent en utilisant une fonction de génération
    en éléments constitués qu'ils retournent alors
"""
from ..base import Element
from ..constants import T_STATE
from typing import TypeVar, Iterator, Type, Callable, List, Dict, Union
import dataclasses

from .MB1 import META_BUILDER_1
from .MB3 import META_BUILDER_3
from .MB4 import META_BUILDER_4
from .MB5 import META_BUILDER_5

E = TypeVar("E", bound=Element)
F = TypeVar("F", bound=Element)


def meta_builder_1(cursor: Callable[[int], F], generator: Callable[[F, E], F], eof: Callable[[int], F]):
    """
    Cette variante gère le cas suivant :
    - éléménts en entrée : liste consécutive non ambigüe
    - éléments en sortie : liste consécutive non ambigüe
    - système d'indexage : inchangé

    :param cursor: Create a cursor at the given index
    :param generator: Generative function of the action to imply and the new state
    :param eof: end of file generator function
    :return:
    """

    def builder(src: Iterator[E]) -> Iterator[F]:
        old: E
        cur: F
        new: F

        cur = cursor(0)

        for old in src:
            while cur.to == old.at:
                new = generator(cur, old)

                if not new.is_terminal:
                    cur = new
                    continue

                if new.is_valid:
                    cur = cursor(new.to)
                    yield new
                    continue

                if old.value == 'EOF':
                    yield eof(old.to)
                    break

                raise SyntaxError((cur, old, new))

    return builder


def meta_builder_2(cursor: Callable[[int], F],
                   generator: Callable[[F, E], F],
                   eof: Callable[[int], F]):
    """
    Cette variante gère le cas suivant :
    - éléménts en entrée : liste consécutive non ambigüe
    - éléments en sortie : liste consécutive non ambigüe
    - système d'indexage : normalisé (un pattern == un saut d'index +1)

    :param cursor: Create a cursor at the given index
    :param generator: Generative function of the action to imply and the new state
    :param eof: end of file generator function
    :return:
    """

    def builder(src: Iterator[E]) -> Iterator[F]:
        pos: int
        old: E
        cur: F
        new: F

        cur = cursor(0)
        pos = 0

        for old in src:
            while cur.to == old.at:
                new = generator(cur, old)

                if not new.is_terminal:
                    cur = new
                    continue

                if new.is_valid:
                    cur = cursor(new.to)
                    yield dataclasses.replace(new, at=pos, to=pos + 1)
                    pos += 1
                    continue

                if old.value == 'EOF':
                    yield eof(old.to)
                    break

                raise SyntaxError((cur, old, new))

    return builder


def meta_builder_3(cursor: Callable[[int], F],
                   generator: Callable[[F, E], F],
                   eof: Callable[[int], F],
                   skips: List[T_STATE]):
    """
    Cette variante gère le cas suivant :
    - éléménts en entrée : liste consécutive non ambigüe
    - éléments en sortie : liste consécutive non ambigüe
    - système d'indexage : normalisé (un pattern == un saut d'index +1)
    - éléments ignorés : pris en compte !

    :param eof:
    :param cursor: Create a cursor at the given index
    :param generator: Generative function of the action to imply and the new state
    :param skips: List of values to ignore while returning terminal outputs
    :return:
    """

    def builder(src: Iterator[E]) -> Iterator[F]:
        cur: F = cursor(0)
        pos: int = 0

        for old in src:
            while cur.to == old.at:
                new: F = generator(cur, old)

                if not new.is_terminal:
                    cur = new
                    continue

                if new.is_valid:
                    cur = cursor(new.to)

                    if new.value in skips:
                        continue
                    else:
                        new = dataclasses.replace(new, at=pos, to=pos + 1)
                        pos += 1

                    yield new
                    continue

                if old.value == 'EOF':
                    yield eof(pos)
                    break

                raise SyntaxError((cur, old, new))

    return builder


def meta_builder_4(cursor: Callable[[int], F],
                   generator: Callable[[F, E], Iterator[F]],
                   eof: Callable[[int], F]):
    """
    Cette variante gère le cas suivant :
    - éléménts en entrée : liste consécutive non ambigüe
    - éléments en sortie : liste consécutive potentiellement ambigüe
    - système d'indexage : inchangé
    - éléments ignorés : pas d'éléments ignorés

    :param eof:
    :param cursor: Create a cursor at the given index
    :param generator: Generative function of the action to imply and the new state
    :return:
    """

    def builder(src: Iterator[E]) -> Iterator[F]:
        old: E
        curs: Dict[int, List[F]]
        new: F

        curs = {}

        def add_cur(cur: F):
            if cur.to not in curs:
                curs[cur.to] = [cur]
            elif cur not in curs[cur.to]:
                curs[cur.to].append(cur)

        add_cur(cursor(0))

        for old in src:
            # if old.at not in curs and old.value != 'EOF':
            #     raise SyntaxError((curs, old))

            queue = curs.get(old.at, [])
            i = 0

            while i < len(queue):
                cur = queue[i]
                i += 1

                for new in generator(cur, old):
                    if not new.is_terminal:
                        add_cur(new)
                        continue

                    if new.is_valid:
                        add_cur(cursor(new.to))
                        yield new
                        continue

            if old.value == 'EOF':
                yield eof(old.to)
                break

    return builder


def meta_builder_5(cursor: Callable[[int], F],
                   generator: Callable[[F, Union[E, F]], Iterator[F]],
                   eof: Callable[[int], F]):
    """
    Cette variante gère le cas suivant :
    - éléménts en entrée : liste consécutive potentiellement ambigüe
    - éléments en sortie : liste consécutive potentiellement ambigüe
    - système d'indexage : inchangé
    - éléments ignorés : pas d'éléments ignorés
    - génération : reflexive, le builder peut piocher dans les éléments qu'il génère

    :param eof:
    :param cursor: Create a cursor at the given index
    :param generator: Generative function of the action to imply and the new state
    :return:
    """

    def builder(src: Iterator[E]) -> Iterator[F]:
        old: E
        curs: Dict[int, List[F]]
        new: F

        curs = {}

        def add_cur(cur: F):
            to = cur.to
            if to not in curs:
                curs[to] = [cur]
            elif cur not in curs[to]:
                curs[to].append(cur)

        add_cur(cursor(0))

        stack = []
        j = 0

        def add_to_stack(obj: Union[E, F]):
            if obj not in stack:
                stack.insert(j, obj)

        for oldb in src:
            stack.append(oldb)

            while j < len(stack):
                old = stack[j]
                j += 1

                if old.at in curs:
                    queue = curs[old.at]
                    add_cur(cursor(old.at))

                    i = 0
                    while i < len(queue):
                        cur = queue[i]
                        i += 1

                        for new in generator(cur, old):
                            if not new.is_terminal:
                                add_cur(new)
                                continue

                            if new.is_valid:
                                add_cur(cursor(new.to))
                                add_to_stack(new)
                                yield new
                                continue

                    continue

            if oldb.value == 'EOF':
                yield eof(oldb.to)
                break

                # raise SyntaxError((curs, old))

        # for i, icurs in curs.items():
        #     print(i, icurs)
        #
        # for j, istck in enumerate(stack):
        #     print(j, istck)

    return builder


FORMAL_INPUTS = 1
FORMAL_OUTPUTS = 2
HAS_SKIPS = 4
REFLEXIVE = 8


def build_func(name: str,
               fun: str,
               formal_inputs: bool,
               formal_outputs: bool,
               reflexive: bool,
               input_cls: Type[Element],
               output_cls: Type[Element],
               skips: List[str] = None):
    has_skips = bool(skips)
    sign = FORMAL_INPUTS * formal_inputs + FORMAL_OUTPUTS * formal_outputs + HAS_SKIPS * has_skips + REFLEXIVE * reflexive

    if sign == FORMAL_INPUTS + FORMAL_OUTPUTS:
        return META_BUILDER_1(name=name, fun=fun, input_cls=input_cls, output_cls=output_cls)
    elif sign == FORMAL_INPUTS + FORMAL_OUTPUTS + HAS_SKIPS:
        return META_BUILDER_3(name=name, fun=fun, input_cls=input_cls, output_cls=output_cls, skips=skips)
    elif sign == FORMAL_INPUTS:
        return META_BUILDER_4(name=name, fun=fun, input_cls=input_cls, output_cls=output_cls)
    elif sign == FORMAL_INPUTS + REFLEXIVE:
        return META_BUILDER_5(name=name, fun=fun, input_cls=input_cls, output_cls=output_cls)
    else:
        raise Exception("invalid parameters combination")


__all__ = ["build_func"]
