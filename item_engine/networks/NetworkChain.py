from .ElementList import ElementList


class NetworkChain:
    def __init__(self, source: ElementList, *networks):
        self.source: ElementList = source
        self.networks = networks

    def __iter__(self):
        for element in self.source:
            layer = [element]
            for network in self.networks:
                layer = network.extend(layer)
            yield from layer
