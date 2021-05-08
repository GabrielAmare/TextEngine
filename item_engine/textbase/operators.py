from typing import Tuple, Union, List, Optional

from item_engine import Group, Match, Branch, All, INF
import python_generator as pg

from .base_materials import Symbol, Keyword

__all__ = ["UNIT", "OP", "ENUM"]


class UNIT:
    def __init__(self, n: str, k: str, t: type, f: pg.LAMBDA = None):
        assert t in (bool, int, float, str)
        self.n: str = n
        self.k: str = k
        self.t: type = t
        self.f: Optional[pg.LAMBDA] = f

    def pg_if(self, cls_name: str) -> pg.IF:
        if self.f is None:
            arg = "e.content"
            prem = []
        else:
            arg = pg.CALL(
                name="parse",
                args=pg.ARGS("e.content")
            )
            prem = [pg.SETATTR(k="parse", v=self.f)]

        return pg.IF(
            cond=pg.EQ("e.value", pg.STR(self.n)),
            body=pg.LINES([
                *prem,
                pg.RETURN(pg.CALL(cls_name, pg.ARGS(pg.CALL(self.t.__name__, pg.ARGS(arg)))))
            ])
        )

    def pg_class(self, cls_name: str) -> pg.CLASS:
        args = [pg.ARG(k=self.k, t=self.t.__name__)]
        return pg.CLASS(
            name=cls_name,
            body=pg.LINES([
                pg.METHODS.INIT(*args),
                pg.METHODS.REPR(*args),
                pg.DEF(
                    name="__str__",
                    args=pg.ARGS(pg.ARG(k="self")),
                    body=pg.LINES([
                        pg.RETURN(f"str(self.{self.k})")
                    ])
                )
            ])
        )


class OP:
    def __init__(self, *childs: Union[Group, Symbol, Keyword]):
        self.childs: Tuple[Union[Group, Symbol, Keyword]] = childs

        self.matches: List[Match] = []
        self.args: List[str] = []
        self.as_str: str = ""

        self.n = 0
        for child in self.childs:
            if isinstance(child, (Symbol, Keyword)):
                self.matches.append(Match(child.tokenG, "include"))
                self.as_str += str(child).replace('{', '{{').replace('}', '}}')
            elif isinstance(child, Group):
                self.matches.append(Match(child, f"as:c{self.n}"))
                self.args.append(f"build(e.data['c{self.n}'])")
                self.as_str += f"{{self.c{self.n}!s}}"
                self.n += 1
            else:
                raise ValueError(child)

    def pg_class(self, cls_name: str):
        args = [pg.ARG(k=f"c{index}") for index in range(self.n)]
        return pg.CLASS(
            name=cls_name,
            body=pg.LINES([
                pg.METHODS.INIT(*args),
                pg.METHODS.REPR(*args),
                pg.DEF(
                    name="__str__",
                    args=pg.ARGS(pg.ARG(k="self")),
                    body=pg.LINES([
                        pg.RETURN(pg.FSTR(self.as_str))
                    ])
                )
            ])
        )

    def pg_if(self, cls_name: str):
        br_name = f"__{cls_name.upper()}__"
        return pg.IF(
            cond=pg.EQ("e.value", pg.STR(br_name)),
            body=pg.RETURN(pg.CALL(
                name=cls_name,
                args=pg.ARGS(*self.args)
            ))
        )

    def branch(self, cls_name: str):
        br_name = f"__{cls_name.upper()}__"
        return Branch(
            name=br_name,
            rule=All(tuple(self.matches)),
            priority=0,
            transfer=False
        )


class ENUM:
    def __init__(self, g: Group, s: Union[Symbol, Keyword]):
        self.g: Group = g
        self.s: Union[Symbol, Keyword] = s

    def pg_class(self, cls_name: str) -> pg.CLASS:
        return pg.CLASS(
            name=cls_name,
            body=pg.LINES(
                [
                    pg.DEF(
                        name="__init__",
                        args=pg.ARGS(pg.ARG(k="self"), pg.ARG(k="*cs")),
                        body=pg.LINES([pg.SETATTR(k=f"self.cs", v="cs")])
                    ),
                    pg.DEF(
                        name="__repr__",
                        args=pg.ARGS(pg.ARG(k="self")),
                        body=pg.LINES([
                            pg.RETURN(pg.FSTR("{self.__class__.__name__}({', '.join(map(repr, self.cs))})"))
                        ])
                    ),
                    pg.DEF(
                        name="__str__",
                        args=pg.ARGS(pg.ARG(k="self")),
                        body=pg.LINES([
                            pg.RETURN(
                                pg.CALL(f"{str(self.s)!r}.join", pg.ARGS(pg.CALL("map", pg.ARGS("str", "self.cs")))))
                        ])
                    )
                ]
            )
        )

    def pg_if(self, cls_name: str) -> pg.IF:
        br_name = f"__{cls_name.upper()}__"
        return pg.IF(
            cond=pg.EQ("e.value", pg.STR(br_name)),
            body=pg.RETURN(pg.CALL(
                name=cls_name,
                args=pg.ARGS("*map(build, e.data['cs'])")
            ))
        )

    def branch(self, cls_name: str):
        br_name = f"__{cls_name.upper()}__"
        return Branch(
            name=br_name,
            rule=Match(self.g, "in:cs") & (Match(self.s.tokenG, "include") & Match(self.g, "in:cs")).repeat(1, INF),
            priority=0,
            transfer=False
        )
