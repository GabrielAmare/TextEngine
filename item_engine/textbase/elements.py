from dataclasses import dataclass, field

from item_engine import Element, ACTION, STATE, INDEX, T_STATE, INCLUDE, EXCLUDE

__all__ = ["Char", "Token", "Lemma"]


class HashableDict(dict):
    def __hash__(self):
        return hash((type(self), tuple(sorted(self.items(), key=lambda item: item[0]))))


@dataclass(frozen=True, order=True)
class BaseElement(Element):
    @classmethod
    def EOF(cls, start: INDEX):
        return cls(
            start=start,
            end=start,
            value=T_STATE("EOF")
        )

    def eof(self):
        return self.__class__.EOF(self.end)

    @property
    def is_eof(self):
        return self.value == "EOF"

    def develop(self, action: ACTION, value: STATE, item: Element) -> Element:
        raise NotImplementedError


@dataclass(frozen=True, order=True)
class Char(BaseElement):
    @classmethod
    def make(cls, index: INDEX, char: str):
        return Char(
            value=T_STATE(char),
            start=index,
            end=index + 1
        )

    def develop(self, action: ACTION, value: STATE, item):
        raise Exception


@dataclass(frozen=True, order=True)
class Token(BaseElement):
    content: str = ""

    def __str__(self):
        return repr(self.content)

    def develop(self, action: ACTION, value: STATE, item: Char):
        if action == INCLUDE:
            return self.__class__(
                start=self.start,
                end=item.end,
                value=value,
                content=self.content + str(item.value)
            )
        elif action == EXCLUDE:
            return self.__class__(
                start=self.start,
                end=self.end,
                value=value,
                content=self.content
            )
        else:
            raise ValueError(action)


@dataclass(frozen=True, order=True)
class Lemma(BaseElement):
    data: HashableDict = field(default_factory=HashableDict)

    def develop(self, action: ACTION, value: STATE, item: Token):
        data = HashableDict(self.data)
        if action == INCLUDE:
            return self.__class__(
                start=self.start,
                end=item.end,
                value=value,
                data=data
            )
        elif action == EXCLUDE:
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
