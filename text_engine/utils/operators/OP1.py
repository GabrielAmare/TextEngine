from ...core import Match, As


class OP1:
    s1: str
    s2: str

    @classmethod
    def _cls(cls, name, s1, s2):
        exec(f"class {name}({cls.__name__}):\n\ts1 = {repr(s1)}\n\ts2 = {repr(s2)}")
        return eval(name)

    def __init__(self, one):
        self.one = one

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.one)})"

    def __str__(self):
        return f"{self.s1}{str(self.one)}{self.s2}"


class OP1B(OP1):
    @classmethod
    def cls(cls, name, s1, s2):
        return cls._cls(name, s1, s2)

    @classmethod
    def builder(cls, name: str, S1: (str, str), I: str, S2: (str, str)):
        return [
            cls.cls(name, S1[0], S2[0]),
            Match(S1[1])
            & As("one", Match(I))
            & Match(S2[1])
        ]


class OP1L(OP1):
    @classmethod
    def cls(cls, name, s2):
        return cls._cls(name, "", s2)

    @classmethod
    def builder(cls, name: str, S1: (str, str), I: str, S2: (str, str)):
        return [
            cls.cls(name, S1[0]),
            Match(S1[1])
            & As("one", Match(I))
        ]


class OP1R(OP1):
    @classmethod
    def cls(cls, name, s1):
        return cls._cls(name, s1, "")

    @classmethod
    def builder(cls, name: str, S1: (str, str), I: str, S2: (str, str)):
        return [
            cls.cls(name, S2[0]),
            As("one", Match(I))
            & Match(S2[1])
        ]


class OP1N(OP1):
    @classmethod
    def cls(cls, name):
        return cls._cls(name, "", "")

    @classmethod
    def builder(cls, name: str, I: str):
        return [
            cls.cls(name),
            As("one", Match(I))
        ]
