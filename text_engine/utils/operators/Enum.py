from ...core import *


class Enum:
    s1: str
    s2: str
    s3: str

    @classmethod
    def _cls(cls, name, s1, s2, s3):
        exec(f"class {name}({cls.__name__}):\n\ts1 = {repr(s1)}\n\ts2 = {repr(s2)}\n\ts3 = {repr(s3)}")
        return eval(name)

    def __init__(self, *items):
        self.items = items

    def __repr__(self):
        return f"{self.__class__.__name__}(" + ", ".join(map(repr, self.items)) + ")"

    def __str__(self):
        return self.s1 + self.s2.join(map(str, self.items)) + self.s3


class EnumB(Enum):
    @classmethod
    def cls(cls, name, s1, s2, s3):
        return cls._cls(name, s1, s2, s3)

    @classmethod
    def builder(cls, name: str, S1: (str, str), I1: str, S2: (str, str), S3: (str, str), backward=False):
        if backward:
            rule = All(Repeat(All(In("*", Match(I1)), Match(S2[1]))), In("*", Match(I1)))
        else:
            rule = All(In("*", Match(I1)), Repeat(All(Match(S2[1]), In("*", Match(I1)))))

        return [
            cls.cls(name, S1[0], S2[0], S3[0]),
            Match(S1[1])
            & rule
            & Match(S3[1])
        ]


class EnumN(Enum):
    @classmethod
    def cls(cls, name, s2):
        return cls._cls(name, "", s2, "")

    @classmethod
    def builder(cls, name: str, I1: str, S2: (str, str), backward=False):
        if backward:
            rule = All(Repeat(All(In("*", Match(I1)), Match(S2[1]))), In("*", Match(I1)))
        else:
            rule = All(In("*", Match(I1)), Repeat(All(Match(S2[1]), In("*", Match(I1)))))

        return [cls.cls(name, S2[0]), rule]
