from dataclasses import dataclass, field
from item_engine import Element, ACTION, STATE

__all__ = ["Char", "Token", "Lemma"]


class HashableDict(dict):
    def __hash__(self):
        return hash((type(self), tuple(sorted(self.items(), key=lambda item: item[0]))))


@dataclass(frozen=True, order=True)
class Char(Element):
    char: str

    @classmethod
    def make(cls, index: int, char: str):
        return Char(
            value="CHAR",
            start=index,
            end=index + 1,
            char=char
        )

    def develop(self, action: ACTION, value: STATE, item):
        raise Exception


@dataclass(frozen=True, order=True)
class Token(Element):
    content: str = ""

    def __str__(self):
        return repr(self.content)

    def develop(self, action: ACTION, value: STATE, item: Char):
        if action == "include":
            return self.__class__(
                start=self.start,
                end=item.end,
                value=value,
                content=self.content + item.char
            )
        elif action == "ignore":
            return self.__class__(
                start=self.start,
                end=self.end,
                value=value,
                content=self.content
            )
        else:
            raise ValueError(action)


@dataclass(frozen=True, order=True)
class Lemma(Element):
    data: HashableDict = field(default_factory=HashableDict)

    def develop(self, action: ACTION, value: STATE, item: Token):
        data = HashableDict(self.data)
        if action == "include":
            return self.__class__(
                start=self.start,
                end=item.end,
                value=value,
                data=data
            )
        elif action == "ignore":
            return self.__class__(
                start=self.start,
                end=self.end,
                value=value,
                data=data
            )
        elif ":" in action:
            action, name = action.split(":", 1)
            if action == "as":
                data[name] = item
            elif action == "in":
                data.setdefault(name, [])
                data[name].append(item)
            else:
                raise ValueError(name)
            return self.__class__(
                start=self.start,
                end=item.end,
                value=value,
                data=data
            )
        else:
            raise ValueError(action)
