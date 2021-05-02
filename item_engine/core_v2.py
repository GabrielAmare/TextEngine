from collections import deque
from typing import Generic, List, Union, Iterator, Optional, Any, Generator, TypeVar, Type, Tuple, Callable, Dict, \
    Iterable, Deque
from dataclasses import dataclass

__all__ = [
    "Element", "Network_",
    "NoBridgeNetwork", "ReflexiveNetwork",
    "ACTION", "NT_STATE", "T_STATE", "STATE", "INDEX", "POSITION",
    "PARSER", "OUTPUT_LAYER",
    "SetList", "PositionRegister"
]

ACTION = str
NT_STATE = int
T_STATE = str
STATE = Union[NT_STATE, T_STATE]
INDEX = int
POSITION = int


@dataclass(frozen=True, order=True)
class Element:
    start: INDEX
    end: INDEX
    value: STATE

    @property
    def terminal(self) -> bool:
        return isinstance(self.value, T_STATE)

    def develop(self, action: ACTION, value: STATE, item):
        raise NotImplementedError


INPUT = TypeVar('INPUT', bound=Element)
OUTPUT = TypeVar('OUTPUT', bound=Element)

OUTPUT_LAYER = List[OUTPUT]

PARSER = Callable[[NT_STATE, INPUT], Iterator[Tuple[ACTION, STATE]]]



T = TypeVar("T")


class SetList(list, Generic[T]):
    def append(self, object: T) -> None:
        if object not in self:
            super().append(object)

    def extend(self, iterable: Iterable[T]) -> None:
        for object in iterable:
            self.append(object)


class PositionRegister:
    def __init__(self):
        self.positions: Dict[INDEX, POSITION] = {}

    def new(self) -> POSITION:
        if self.positions:
            return max(self.positions.values()) + 1
        else:
            return 0

    def get(self, index: INDEX) -> POSITION:
        if index in self.positions:
            return self.positions[index]
        else:
            self.positions[index] = position = self.new()
            return position

    def merge(self, p1: POSITION, p2: POSITION) -> None:
        """
            With ``mn``/``mx`` resp. the minimum/maximum of ``p1`` and ``p2``
            For any index pointing at position ``mn``, make it point to ``mx``
        """
        mx = max(p1, p2)
        mn = min(p1, p2)
        for index, position in self.positions.items():
            if position == mn:
                self.positions[index] = mx


class Network_(Generic[INPUT, OUTPUT]):
    pr: PositionRegister

    def __iter__(self) -> Generator[OUTPUT, None, None]:
        raise NotImplementedError


class NoBridgeNetwork(Network_, Generic[INPUT, OUTPUT]):
    """Network implementation without bridges"""

    def __init__(self, output_cls: Type[OUTPUT], parser: PARSER):
        self.output_cls: Type[OUTPUT] = output_cls
        self.non_terminal: List[OUTPUT] = []
        self.terminal: List[OUTPUT] = []
        self.parser = parser
        self.source: Optional[Iterator[INPUT]] = None

    def __iter__(self) -> Generator[OUTPUT, None, None]:
        assert self.source is not None

        for input_element in self.source:
            for output_element in self.add(input_element):
                yield output_element

    def new_cursor(self, index: INDEX) -> None:
        self.non_terminal.append(self.output_cls(start=index, end=index, value=0))

    def can_continue_from(self, element: INPUT) -> bool:
        return any(self.are_connected(nt, element) for nt in self.non_terminal)

    def can_start_with(self, element: INPUT) -> bool:
        return any(self.are_connected(t, element) for t in self.terminal)

    def add(self, i: INPUT) -> List[OUTPUT]:
        assert i.terminal
        if self.can_start_with(i):
            self.new_cursor(i.start)
            can_continue = True
        else:
            can_continue = self.can_continue_from(i)

        terminals: List[OUTPUT] = []
        if can_continue:
            for o in self.non_terminal:
                if self.are_connected(o, i):
                    for g in self.generate_from(o, i):
                        if g.terminal:
                            self.terminal.append(g)
                            terminals.append(g)
                        else:
                            self.non_terminal.append(g)

        return terminals

    def are_connected(self, o: OUTPUT, i: INPUT) -> bool:
        """Return True if the two elements are following each other"""
        return o.end == i.start

    def generate_from(self, o: OUTPUT, i: INPUT) -> Iterator[OUTPUT]:
        """Return the new outputs generated from the ``origin`` output and a ``target`` input"""
        for action, value in self.parser(o.value, i):
            yield o.develop(action, value, i)

    def feed_iterator(self, iterator: Iterator[INPUT]):
        """Give the Network a source of input items"""
        self.source = iterator

    def feed_network(self, network: Network_[Any, INPUT]):
        """Give the Network a source using another network"""
        self.feed_iterator(iter(network))


class ReflexiveNetwork(Network_, Generic[INPUT, OUTPUT]):
    """Network implementation with bridges and being reflexive (using itself to build itself)"""

    def __init__(self, output_cls: Type[OUTPUT], parser: PARSER, to_ignore=None):
        if to_ignore is None:
            to_ignore = []
        self.output_cls: Type[OUTPUT] = output_cls
        self.non_terminals: SetList[OUTPUT] = SetList()
        self.terminals: SetList[OUTPUT] = SetList()
        self.parser = parser
        self.network_source: Optional[Network[Any, INPUT]] = None
        self.source: Optional[Iterator[INPUT]] = None
        self.to_ignore: List[T_STATE] = to_ignore

        self.positions: Dict[INDEX, POSITION] = {}
        self.pr = PositionRegister()

        self.most_recent: Deque[OUTPUT] = deque()

    def __iter__(self) -> Generator[OUTPUT, None, None]:
        assert self.source is not None

        for input_element in self.source:
            yield from self.add(input_element)

    def new_cursor(self, index: INDEX) -> None:
        self.non_terminals.append(self.output_cls(start=index, end=index, value=0))

    def can_continue_from(self, element: Union[INPUT, OUTPUT]) -> bool:
        return any(self.are_connected(nt, element) for nt in self.non_terminals)

    def can_start_with(self, element: Union[INPUT, OUTPUT]) -> bool:
        return element.start == 0 or any(self.are_connected(t, element) for t in self.terminals)

    def add_bridge(self, o: OUTPUT) -> None:
        """Use the output ``o`` to make a bridge"""
        a: POSITION = self.pr.get(o.start)
        b: POSITION = self.pr.get(o.end)
        self.pr.merge(a, b)

    def gen_from(self, i: INPUT):
        Te: SetList[OUTPUT] = SetList()
        NT: SetList[OUTPUT] = SetList()
        Br: SetList[OUTPUT] = SetList()

        for o in self.non_terminals:
            if self.are_connected(o, i):
                for g in self.generate_from(o, i):
                    if not g.terminal:
                        NT.append(g)
                    elif g.value in self.to_ignore:
                        Br.append(g)
                    elif not g.value.startswith('!'):
                        Te.append(g)

        return Te, NT, Br

    def add(self, i: Union[INPUT, OUTPUT]) -> OUTPUT_LAYER:
        """
        Given an input element, this method return all the terminal elements that can be built from the input,
        considering we can finish the non-terminal previous elements,
        also, this method store the non-terminal elements for the next use
        :param i:
        :return:
        """
        assert i.terminal
        if self.can_start_with(i):
            self.new_cursor(i.start)
            can_continue = True
        else:
            self.new_cursor(i.start)
            can_continue = self.can_continue_from(i)

        todo: Deque[Union[INPUT, OUTPUT]] = deque()  # ADD
        todo.append(i)  # ADD
        done: SetList[Union[INPUT, OUTPUT]] = SetList()  # ADD

        terminals: SetList[OUTPUT] = SetList()

        while todo:  # ADD
            i = todo.popleft()  # ADD
            done.append(i)  # ADD
            if can_continue:
                Te, NT, Br = self.gen_from(i)
                terminals.extend(Te)
                self.non_terminals.extend(NT)
                for e in Br:
                    self.add_bridge(e)
                for o in self.non_terminals:
                    if self.are_connected(o, i):
                        for g in self.generate_from(o, i):
                            if g.terminal:
                                if g.value in self.to_ignore:
                                    self.add_bridge(g)
                                else:
                                    if not g.value.startswith('!'):
                                        terminals.append(g)
                                        if g not in done:  # ADD
                                            todo.append(g)  # ADD
                            else:
                                self.non_terminals.append(g)

        # non overlaps
        result = []
        for t in terminals:
            if not any(r.value == t.value for r in result):
                result.append(t)

        self.terminals.extend(result)
        return result

    def are_connected(self, o: OUTPUT, i: INPUT) -> bool:
        """Return True if the two elements are following each other"""
        p1: POSITION = self.pr.get(o.end)
        p2: POSITION = self.pr.get(i.start)
        return p1 == p2

    def generate_from(self, o: OUTPUT, i: INPUT) -> Iterator[OUTPUT]:
        """Return the new outputs generated from the ``origin`` output and a ``target`` input"""
        for action, value in self.parser(o.value, i):
            yield o.develop(action, value, i)

    def feed_iterator(self, iterator: Iterator[INPUT]):
        """Give the Network a source of input items"""
        self.source = iterator

    def feed_network(self, network: Network_[Any, INPUT]):
        """Give the Network a source using another network"""
        self.pr = network.pr
        self.feed_iterator(iter(network))
