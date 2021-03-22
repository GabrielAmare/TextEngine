class Identified:
    identifier: str
    ALL = "*"
    SEP = "."

    def __init__(self, identifier: str):
        self.identifier = identifier
        self.name, *self.groups = identifier.split(self.SEP)

    def __eq__(self, identified):
        name, *groups = identified.identifier.split(self.SEP)
        return name == self.name and set(groups) == set(self.groups)

    def __le__(self, identifier: str):
        if isinstance(identifier, Identified):
            identifier = identifier.identifier
        name, *groups = identifier.split(self.SEP)
        return name in (self.ALL, self.name) and all(group in self.groups for group in groups)

    def __ge__(self, identifier: str):
        if isinstance(identifier, Identified):
            identifier = identifier.identifier
        name, *groups = identifier.split(self.SEP)
        return self.name in (self.ALL, name) and all(group in groups for group in self.groups)
