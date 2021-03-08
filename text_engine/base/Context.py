class Context:
    pile: list
    data: dict

    def __init__(self, *pile, _=None, **data):
        self.root = _
        self.pile = list(pile)
        self.data = dict(data)

    def add_item(self, item):
        self.pile.append(item)

    def key_set(self, key, val):
        self.data[key] = val

    def key_add(self, key, val):
        self.data.setdefault(key, [])
        self.data[key].append(val)

    def __setitem__(self, key, val):
        self.key_set(key, val)

    def pop_last(self):
        return self.pile.pop(-1)

    def sub_context(self, *pile, **data):
        return Context(*pile, _=self, **data)
