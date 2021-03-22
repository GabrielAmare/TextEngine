from ...core import Match, As


class OP2:
    s1: str
    s2: str
    s3: str

    @classmethod
    def _cls(cls, name, s1, s2, s3):
        exec(f"class {name}({cls.__name__}):\n\ts1 = {repr(s1)}\n\ts2 = {repr(s2)}\n\ts3 = {repr(s3)}")
        return eval(name)

    def __init__(self, one, two):
        self.one = one
        self.two = two

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.one)}, {repr(self.two)})"

    def __str__(self):
        return f"{self.s1}{str(self.one)}{self.s2}{str(self.two)}{self.s3}"

    @classmethod
    def _cls(cls, name, s1, s2, s3):
        exec(f"class {name}({cls.__name__}):\n\ts1 = {repr(s1)}\n\ts2 = {repr(s2)}\n\ts3 = {repr(s3)}")
        return eval(name)


class OP2B(OP2):

    @classmethod
    def cls(cls, name, s1, s2, s3):
        return cls._cls(name, s1, s2, s3)

    @classmethod
    def builder(cls, name: str, S1: (str, str), I1: str, S2: (str, str), I2: str, S3: (str, str)):
        return [
            cls.cls(name, S1[0], S2[0], S3[0]),
            Match(S1[1])
            & As("one", Match(I1))
            & Match(S2[1])
            & As("two", Match(I2))
            & Match(S3[1])
        ]


class OP2L(OP2):
    @classmethod
    def cls(cls, name, s1, s2):
        return cls._cls(name, s1, s2, "")

    @classmethod
    def builder(cls, name: str, S1: (str, str), I1: str, S2: (str, str), I2: str):
        return [
            cls.cls(name, S1[0], S2[0]),
            Match(S1[1])
            & As("one", Match(I1))
            & Match(S2[1])
            & As("two", Match(I2))
        ]


class OP2R(OP2):
    @classmethod
    def cls(cls, name, s2, s3):
        return cls._cls(name, "", s2, s3)

    @classmethod
    def builder(cls, name: str, I1: str, S2: (str, str), I2: str, S3: (str, str)):
        return [
            cls.cls(name, S2[0], S3[0]),
            As("one", Match(I1))
            & Match(S2[1])
            & As("two", Match(I2))
            & Match(S3[1])
        ]


class OP2N(OP2):
    @classmethod
    def cls(cls, name, s2):
        return cls._cls(name, "", s2, "")

    @classmethod
    def builder(cls, name: str, I1: str, S2: (str, str), I2: str):
        return [
            cls.cls(name, S2[0]),
            As("one", Match(I1))
            & Match(S2[1])
            & As("two", Match(I2))
        ]
