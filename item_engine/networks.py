from typing import Generic, List, Iterator, Optional, Generator, Type, Tuple, TypeVar, Union, Callable

from tools37 import ReprTable

from item_engine.core_v2 import Element, PositionRegister, SetList

__all__ = ["Network", "ReflexiveNetwork"]

ACTION = str
NT_STATE = int
T_STATE = str
STATE = Union[NT_STATE, T_STATE]
INDEX = int
POSITION = int

INPUT = TypeVar('INPUT', bound=Element)
OUTPUT = TypeVar('OUTPUT', bound=Element)

OUTPUT_LAYER = List[OUTPUT]

PARSER = Callable[[NT_STATE, INPUT], Iterator[Tuple[ACTION, STATE]]]


def shouldnt_be_called_twiced(function):
    return function
    already = []

    def wrapped(*args, **kwargs):
        key = (args, kwargs)
        if key in already:
            raise Exception(f"the function {function} should not be called twice with arguments {key}")
        else:
            already.append(key)
            return function(*args, **kwargs)

    return wrapped


class BaseNetwork:
    def __init__(self, parser: PARSER, output_cls: Type[OUTPUT]):
        self.non_terminals: List[Element] = []
        self.terminals: List[Element] = []

        self.parser: PARSER = parser
        self.output_cls: Type[OUTPUT] = output_cls
        self.source: Optional[Iterator[INPUT]] = None

    @shouldnt_be_called_twiced
    def elements_before(self, i: INPUT) -> Iterator[OUTPUT]:
        """Yields the non-terminal elements that ends where ``i`` starts"""
        for o in self.non_terminals:
            if self.are_connected(o, i):
                yield o

    @shouldnt_be_called_twiced
    def are_connected(self, o: OUTPUT, i: INPUT) -> bool:
        """Return True if ``o`` ends where ``i`` starts"""
        raise NotImplementedError

    @shouldnt_be_called_twiced
    def generate_from(self, o: OUTPUT, i: INPUT) -> Iterator[OUTPUT]:
        """Return the new outputs generated from the ``origin`` output and a ``target`` input"""
        for action, value in self.parser(o.value, i):
            yield o.develop(action, value, i)

    @shouldnt_be_called_twiced
    def new_cursor(self, index: INDEX) -> None:
        """Create a new empty non-terminal element at ``index``"""
        self.non_terminals.append(self.output_cls(start=index, end=index, value=0))

    @shouldnt_be_called_twiced
    def can_continue_from(self, i: INPUT) -> bool:
        """Return True if any non-terminal element ends where ``i`` starts"""
        return any(self.are_connected(nt, i) for nt in self.non_terminals)

    @shouldnt_be_called_twiced
    def can_start_with(self, i: INPUT) -> bool:
        """Return True if any terminal element ends where ``i`` starts"""
        return i.start == 0 or any(self.are_connected(t, i) for t in self.terminals)

    @shouldnt_be_called_twiced
    def feed_iterator(self, iterator: Iterator[INPUT]):
        """Give the Network a source of input items"""
        self.source = iterator

    def confirm_non_terminals(self, non_terminals: SetList[OUTPUT]) -> None:
        self.non_terminals.extend(non_terminals)

    def confirm_terminals(self, terminals: SetList[OUTPUT]) -> OUTPUT_LAYER:
        """Filter the terminal elements which are not to save, save the other and return them"""
        # non overlaps
        result = []
        for t in terminals:
            if any(r.value == t.value for r in result):
                continue

            if any(r.start < t.start for r in terminals if r.end == t.end):
                continue

            result.append(t)

        self.terminals.extend(result)
        return result


class WithBridges(BaseNetwork):
    def __init__(self, parser: PARSER, output_cls: Type[OUTPUT], to_ignore=None):
        super().__init__(parser, output_cls)
        if to_ignore is None:
            to_ignore = []

        self.pr: PositionRegister = PositionRegister()
        self.to_ignore: List[T_STATE] = to_ignore

    def add_bridges(self, outputs: SetList[OUTPUT]) -> None:
        """Use the ``outputs`` to make bridges"""
        for o in outputs:
            a: POSITION = self.pr.get(o.start)
            b: POSITION = self.pr.get(o.end)
            self.pr.merge(a, b)

    @shouldnt_be_called_twiced
    def are_connected(self, o: OUTPUT, i: INPUT) -> bool:
        """Return True if ``o`` ends where ``i`` starts"""
        return self.pr.get(o.end) == self.pr.get(i.start)

    @shouldnt_be_called_twiced
    def gen(self, i: INPUT) -> OUTPUT_LAYER:
        """Generate bridge, non-terminal and terminal elements from the input ``i``"""
        non_terminals: SetList[OUTPUT] = SetList()
        bridges: SetList[OUTPUT] = SetList()
        terminals: SetList[OUTPUT] = SetList()

        for o in self.elements_before(i):
            for g in self.generate_from(o, i):
                if not g.terminal:
                    non_terminals.append(g)
                elif g.value in self.to_ignore:
                    bridges.append(g)
                elif not g.value.startswith('!'):
                    terminals.append(g)
                else:
                    pass  # ignore the invalid terminal outputs

        self.add_bridges(bridges)
        self.confirm_non_terminals(non_terminals)
        return self.confirm_terminals(terminals)

    @shouldnt_be_called_twiced
    def feed_network(self, network):
        """Give the Network a source using another network"""
        assert isinstance(network, Network)
        self.pr = network.pr
        self.feed_iterator(iter(network))

    def terminal_table(self, **config):
        return ReprTable.from_items(
            items=self.terminals,
            config={
                "start": lambda o: str(self.pr.get(o.start)),
                "end": lambda o: str(self.pr.get(o.end)),
                "value": lambda o: str(o.value),
                **config
            }
        )

    def non_terminal_table(self, **config):
        return ReprTable.from_items(
            items=self.non_terminals,
            config={
                "start": lambda o: str(self.pr.get(o.start)),
                "end": lambda o: str(self.pr.get(o.end)),
                "value": lambda o: str(o.value),
                **config
            }
        )


class WithoutBridges(BaseNetwork):
    @shouldnt_be_called_twiced
    def are_connected(self, o: OUTPUT, i: INPUT) -> bool:
        """Return True if ``o`` ends where ``i`` starts"""
        return o.end == i.start

    @shouldnt_be_called_twiced
    def feed_network(self, network):
        """Give the Network a source using another network"""
        assert isinstance(network, Network)
        self.feed_iterator(iter(network))

    @shouldnt_be_called_twiced
    def gen(self, i: INPUT) -> OUTPUT_LAYER:
        """Generate non-terminal and terminal elements from the input ``i``"""
        non_terminals: SetList[OUTPUT] = SetList()
        terminals: SetList[OUTPUT] = SetList()

        for o in self.elements_before(i):
            for g in self.generate_from(o, i):
                if not g.terminal:
                    non_terminals.append(g)
                elif not g.value.startswith('!'):
                    terminals.append(g)
                else:
                    pass  # ignore the invalid terminal outputs

        self.confirm_non_terminals(non_terminals)
        return self.confirm_terminals(terminals)


class Network(WithBridges, Generic[INPUT, OUTPUT]):
    """Network implementation with bridges"""

    def __init__(self, output_cls: Type[OUTPUT], parser: PARSER, to_ignore=None, allow_gaps: bool = True):
        WithBridges.__init__(self, parser, output_cls, to_ignore)

        self.allow_gaps: bool = allow_gaps

    def __iter__(self) -> Generator[OUTPUT, None, None]:
        """Yields all the terminal elements that can be generated from the ``source``"""
        assert self.source is not None
        for input_element in self.source:
            yield from self.append(input_element)

    @shouldnt_be_called_twiced
    def on(self, i: INPUT) -> bool:
        """
            If any terminal element ends where i starts, it creates a new empty non-terminal element
            If any non-terminal element ends where i starts, it return True
        """
        if self.can_start_with(i) or self.allow_gaps:
            self.new_cursor(i.start)
            return True
        else:
            return self.can_continue_from(i)

    @shouldnt_be_called_twiced
    def append(self, i: INPUT) -> OUTPUT_LAYER:
        """
            Return all the terminal elements generated considering the input ``i``
        """
        assert i.terminal

        if self.on(i):
            return self.gen(i)
        else:
            return []


class ReflexiveNetwork(Network, Generic[INPUT, OUTPUT]):
    @shouldnt_be_called_twiced
    def append(self, i: INPUT) -> OUTPUT_LAYER:
        """
            Return all the terminal elements generated considering the input ``i``
        """
        n = 0
        todo: List[Union[INPUT, OUTPUT]] = [i]
        done: OUTPUT_LAYER = []
        while n < len(todo):
            i = todo[n]
            assert i.terminal

            if self.on(i):
                for o in self.gen(i):
                    if o not in todo:
                        todo.append(o)
                    if o not in done:
                        done.append(o)
            n += 1

        return done
