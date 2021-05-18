from typing import Generic, List, Iterator, Optional, Generator, Type, Tuple, TypeVar, Union, Callable

from tools37 import ReprTable

from .Network import Network

from ..constants import ACTION, NT_STATE, T_STATE, STATE, INDEX, POSITION
from ..base import Element
from ..utils import PositionRegister, SetList

__all__ = ["ReflexiveNetwork"]

INPUT = TypeVar('INPUT', bound=Element)
OUTPUT = TypeVar('OUTPUT', bound=Element)

OUTPUT_LAYER = List[OUTPUT]

PARSER = Callable[[NT_STATE, INPUT], Iterator[Tuple[ACTION, STATE]]]


class ReflexiveNetwork(Generic[INPUT, OUTPUT]):
    def __init__(self,
                 function: PARSER,  # the parser function
                 input_cls: Type[INPUT],  # the input required element class
                 output_cls: Type[OUTPUT],  # the output required element class
                 to_ignore=None,  # list of the terminal values to ignore (make a bridge)
                 allow_gaps: bool = True,  # allow gaps between tokens positions
                 # save_terminals: bool = False,  # allow to display the table in the end
                 # remove_previous: bool = True  # this will soften the memory requirement of the network
                 ):
        if to_ignore is None:
            to_ignore = []
        self.non_terminals: List[Element] = []
        self.terminals: List[Element] = []

        self.function: PARSER = function
        self.input_cls: Type[INPUT] = input_cls
        self.output_cls: Type[OUTPUT] = output_cls
        self.source: Optional[Iterator[INPUT]] = None

        self.pr: PositionRegister = PositionRegister()
        self.to_ignore: List[T_STATE] = to_ignore

        self.allow_gaps: bool = allow_gaps

    def add_bridges(self, outputs: SetList[OUTPUT]) -> None:
        """Use the ``outputs`` to make bridges"""
        for o in outputs:
            a: POSITION = self.pr.get(o.at)
            b: POSITION = self.pr.get(o.to)
            self.pr.merge(a, b)

    def are_connected(self, o: OUTPUT, i: INPUT) -> bool:
        """Return True if ``o`` ends where ``i`` starts"""
        return self.pr.get(o.to) == self.pr.get(i.at)

    def gen(self, i: INPUT) -> OUTPUT_LAYER:
        """Generate bridge, non-terminal and terminal elements from the input ``i``"""
        non_terminals: SetList[OUTPUT] = SetList()
        bridges: SetList[OUTPUT] = SetList()
        terminals: SetList[OUTPUT] = SetList()

        for o in self.elements_before(i):
            for g in self.generate_from(o, i):
                if not g.is_terminal:
                    non_terminals.append(g)
                elif g.value in self.to_ignore:
                    bridges.append(g)
                elif not str(g.value).startswith('!'):
                    terminals.append(g)
                else:
                    pass  # ignore the invalid terminal outputs

        self.add_bridges(bridges)
        self.confirm_non_terminals(non_terminals)
        return self.confirm_terminals(terminals)

    def feed_network(self, network):
        """Give the Network a source using another network"""
        assert isinstance(network, Network)
        self.pr = network.pr
        self.feed_iterator(iter(network))

    def terminal_table(self, **config):
        return ReprTable.from_items(
            items=self.terminals,
            config={
                "at": lambda o: str(self.pr.get(o.at)),
                "to": lambda o: str(self.pr.get(o.to)),
                "value": lambda o: str(o.value),
                **config
            }
        )

    def non_terminal_table(self, **config):
        return ReprTable.from_items(
            items=self.non_terminals,
            config={
                "at": lambda o: str(self.pr.get(o.at)),
                "to": lambda o: str(self.pr.get(o.to)),
                "value": lambda o: str(o.value),
                **config
            }
        )

    def elements_before(self, i: INPUT) -> Iterator[OUTPUT]:
        """Yields the non-terminal elements that ends where ``i`` starts"""
        for o in self.non_terminals:
            if self.are_connected(o, i):
                yield o

    def generate_from(self, o: OUTPUT, i: INPUT) -> Iterator[OUTPUT]:
        """Return the new outputs generated from the ``origin`` output and a ``target`` input"""
        for action, value in self.function(o, i):
            yield o.develop(action, value, i)

    def new_cursor(self, index: INDEX) -> None:
        """Create a new empty non-terminal element at ``index``"""
        self.non_terminals.append(self.output_cls(at=index, to=index, value=0))

    def can_continue_from(self, i: INPUT) -> bool:
        """Return True if any non-terminal element ends where ``i`` starts"""
        return any(self.are_connected(nt, i) for nt in self.non_terminals)

    def can_start_with(self, i: INPUT) -> bool:
        """Return True if any terminal element ends where ``i`` starts"""
        return i.at == 0 or any(self.are_connected(t, i) for t in self.terminals)

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

            if any(r.at < t.at for r in terminals if r.to == t.to):
                continue

            result.append(t)

        self.terminals.extend(result)
        return result

    def __iter__(self) -> Generator[OUTPUT, None, None]:
        """Yields all the terminal elements that can be generated from the ``source``"""
        assert self.source is not None
        to = 0
        for input_element in self.source:
            yield from self.append(input_element)
            to = input_element.to
        yield from self.append(self.input_cls.EOF(to))

    def on(self, i: INPUT) -> bool:
        """
            If any terminal element ends where i starts, it creates a new empty non-terminal element
            If any non-terminal element ends where i starts, it return True
        """
        if self.can_start_with(i) or self.allow_gaps:
            self.new_cursor(i.at)
            return True
        else:
            return self.can_continue_from(i)

    def append(self, i: INPUT) -> OUTPUT_LAYER:
        """
            Return all the terminal elements generated considering the input ``i``
        """
        n = 0
        todo: List[Union[INPUT, OUTPUT]] = [i]
        done: OUTPUT_LAYER = []
        while n < len(todo):
            i = todo[n]
            assert i.is_terminal

            if self.on(i):
                for o in self.gen(i):
                    if o not in todo:
                        todo.append(o)
                    if o not in done:
                        done.append(o)
            n += 1

        return done
