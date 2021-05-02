from typing import Callable, Type, DefaultDict, Generic, TypeVar, List, Union, Iterator, Tuple, Optional, Dict
from collections import defaultdict
from dataclasses import dataclass

__all__ = ("Element", "Network", "Engine", "RecursiveEngine")

from item_engine.DAG import DAG, Node, Link


@dataclass(frozen=True, order=True)
class Element:
    start: int
    end: int
    value: Union[int, str]

    @property
    def terminal(self) -> bool:
        return isinstance(self.value, str)

    def develop(self, key: str, value: Union[int, str], item):
        raise NotImplementedError


class Network:
    def __init__(self, to_ignore: Optional[List[str]] = None):
        self.elements: List[Element] = []
        self.to_ignore: List[str] = [] if to_ignore is None else to_ignore

        self.start = 0
        self.end = 0

        self.forward_bridges: DefaultDict[int, List[int]] = defaultdict(list)
        self.backward_bridges: DefaultDict[int, List[int]] = defaultdict(list)

    def __contains__(self, element: Element) -> bool:
        return element in self.elements

    def add(self, element: Element) -> None:
        self.start = min(element.start, self.start)
        self.end = max(element.end, self.end)

        if element.value in self.to_ignore:
            start = element.start
            end = element.end
            self.forward_bridges[start].append(end)
            self.backward_bridges[end].append(start)
        else:
            if element not in self.elements:
                self.elements.append(element)

    def indexes_before(self, n: int) -> List[int]:
        indexes: List[int] = [n]
        for index in self.backward_bridges[n]:
            for newer in self.indexes_before(index):
                if newer not in indexes:
                    indexes.append(newer)
        return indexes

    def indexes_after(self, n: int) -> List[int]:
        indexes: List[int] = [n]
        for index in self.forward_bridges[n]:
            for newer in self.indexes_after(index):
                if newer not in indexes:
                    indexes.append(newer)
        return indexes

    def get_from_start(self, start: int) -> List[Element]:
        """Return all the items which starts at the adress ``start``"""
        return [
            item
            for index in self.indexes_after(start)
            for item in self.elements
            if item.start == index
        ]

    def get_from_end(self, end: int) -> List[Element]:
        """Return all the items which ends at the adress ``end``"""
        return [
            item
            for index in self.indexes_before(end)
            for item in self.elements
            if item.end == index
        ]

    def as_dag(self, fp: str = ""):
        dag = DAG()

        START = dag.start(self.start)
        END = dag.end(self.end)

        nodes: Dict[Element, Node] = {}

        for element in self.elements:
            nodes[element] = dag.text(
                "\n".join([
                    element.__class__.__name__,
                    f"[{element.start}, {element.end}]",
                    str(element.value),
                    str(element)
                ])
            )

        def set_link(origin: Node, target: Node):
            key = (origin, target)
            if key not in links:
                links[key] = dag.link(*key)

        links: Dict[Tuple[Node, Node], Link] = {}
        for origin in self.elements:
            if origin in nodes:
                if self.start in self.indexes_before(origin.start):
                    set_link(START, nodes[origin])

                if self.end in self.indexes_after(origin.end):
                    set_link(nodes[origin], END)

                for target in self.get_from_start(origin.end):
                    if target in nodes:
                        set_link(nodes[origin], nodes[target])

        if self.end in self.indexes_after(self.start):
            set_link(START, END)

        dag.display(splines="normal", ranksep=0.4, view=False, fp=fp)


CTV = TypeVar("CTV", bound=Element)  # generic type for the constitutive elements
CTD = TypeVar("CTD", bound=Element)  # generic type for the constitued elements


class Engine(Generic[CTV, CTD]):
    def __init__(self,
                 parser: Callable[[int, CTV], Iterator[Tuple[str, Union[str, int]]]],
                 ctv: Type[CTV], ctd: Type[CTD],
                 ignore=None
                 ):
        if ignore is None:
            ignore = []
        self.parser = parser
        self.ctv: Type[CTV] = ctv
        self.ctd: Type[CTD] = ctd

        self.network: Network = Network(to_ignore=ignore)

    def __call__(self, ctv_network: Network):
        print(ctv_network.elements)
        ctd_network: Network = Network()
        valid_starts: List[int] = [ctd_network.end]  # ADD

        for ctv in ctv_network.elements:
            if ctd_network.indexes_before(ctv.start):  # ADD
                ctd_network.add(
                    self.ctd(
                        start=ctv.start,
                        end=ctv.start,
                        value=0
                    )
                )

            for old_ctd in ctd_network.get_from_end(ctv.start):
                potential = []
                for action, value in self.parser(old_ctd.value, ctv):
                    new_ctd = old_ctd.develop(action, value, ctv)
                    if new_ctd.terminal:
                        if not new_ctd.value.startswith("!"):
                            potential.append(new_ctd)
                    else:
                        ctd_network.add(new_ctd)

                for ctd in potential:
                    if ctd.start in valid_starts:  # ADD
                        yield ctd
                        valid_starts.append(ctd.end)

        self.network = ctd_network


class RecursiveEngine(Generic[CTV, CTD]):
    def __init__(self,
                 parser: Callable[[CTD, CTV], Iterator[CTD]],
                 ctv: Type[CTV], ctd: Type[CTD],
                 ignore=None
                 ):
        if ignore is None:
            ignore = []
        self.parser = parser
        self.ctv: Type[CTV] = ctv
        self.ctd: Type[CTD] = ctd
        self.ignore = ignore

        self.network: Network = Network()

    def __call__(self, elements: Iterator[Element]):
        ctv_network: Network = Network()
        ctd_network: Network = Network()

        for ctv in elements:
            ctv_network.append(ctv)
            if ctv.value in self.ignore:
                ctd_network.add_bridge(ctv.start, ctv.end)
                continue

        found = 1
        turns = 0
        total = 0
        while found:
            found = 0
            turns += 1
            for ctv in ctv_network.elements:
                # print("ctv", ctv)
                ctd_network.append(
                    self.ctd(
                        start=ctv.start,
                        end=ctv.start,
                        value=0
                    )
                )

                for old_ctd in ctd_network.get_end(ctv.start):
                    # print("old_ctd", old_ctd)
                    # for new_ctd in self.parser(old_ctd, ctv):
                    for action, value in self.parser(old_ctd, ctv):
                        new_ctd = old_ctd.develop(action, value, ctv)
                        # print("new_ctd", new_ctd, "caused by", ctv)
                        if new_ctd.terminal:
                            if not new_ctd.value.startswith("!"):
                                if new_ctd not in ctv_network.elements:
                                    found += 1
                                    total += 1
                                    ctv_network.append(new_ctd)
                                    yield new_ctd
                        else:
                            ctd_network.append(new_ctd)

        print()
        print(f"turns : {turns!r}, found in total : {total!r}")
        # for index in sorted(set(item.start for item in ctd_network.items)):
        #     print(f"start : {index!r}")
        #     for item in ctd_network.items:
        #         if item.start == index:
        #             print(f"  > {item!r}")

        self.network = ctd_network
