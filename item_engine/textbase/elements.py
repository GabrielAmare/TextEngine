from item_engine import Element, ACTION, STATE, INDEX, T_STATE, INCLUDE, EXCLUDE

__all__ = ["Char", "Token", "Lemma"]


class HashableDict(dict):
    def __hash__(self):
        return hash((type(self), tuple(sorted(self.items(), key=lambda item: item[0]))))


class BaseElement(Element):
    @classmethod
    def EOF(cls, start: INDEX):
        return cls(
            start=start,
            end=start,
            value=T_STATE("EOF")
        )

    def develop(self, action: ACTION, value: STATE, item: Element) -> Element:
        raise NotImplementedError


class Char(BaseElement):
    def __hash__(self) -> int:
        return hash((type(self), self.start, self.end, self.value))

    @classmethod
    def make(cls, index: INDEX, char: str):
        return Char(
            value=T_STATE(char),
            start=index,
            end=index + 1
        )

    def develop(self, action: ACTION, value: STATE, item):
        raise Exception


class Token(BaseElement):
    def __init__(self, start: INDEX, end: INDEX, value: STATE, content: str = ""):
        super().__init__(start, end, value)
        self.content: str = content

    def __hash__(self) -> int:
        return hash((type(self), self.start, self.end, self.value, self.content))

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


class Lemma(BaseElement):
    def __init__(self, start: INDEX, end: INDEX, value: STATE, data=None):
        super().__init__(start, end, value)
        if data is None:
            data = {}
        self.data: HashableDict = HashableDict(**data)

    def __hash__(self) -> int:
        return hash((type(self), self.start, self.end, self.value, self.data))

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
