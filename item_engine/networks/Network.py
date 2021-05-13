from typing import Generic, List, Iterator, Optional, Generator, Type, Tuple, TypeVar, Callable, Set, Dict

from tools37 import ReprTable

from ..constants import ACTION, NT_STATE, T_STATE, STATE, INDEX, POSITION
from ..base import Element
from ..utils import PositionRegister, SetList

__all__ = ["Network"]

INPUT = TypeVar('INPUT', bound=Element)
OUTPUT = TypeVar('OUTPUT', bound=Element)

OUTPUT_LAYER = List[OUTPUT]

FUNCTION = Callable[[NT_STATE, INPUT], Iterator[Tuple[ACTION, STATE]]]


class Network(Generic[INPUT, OUTPUT]):
    """Network implementation with bridges"""

    def __init__(self,
                 function: FUNCTION,  # the parser function
                 input_cls: Type[INPUT],  # the input required element class
                 output_cls: Type[OUTPUT],  # the output required element class
                 to_ignore=None,  # list of the terminal values to ignore (make a bridge)
                 allow_gaps: bool = True,  # allow gaps between tokens positions
                 save_terminals: bool = False,  # allow to display the table in the end
                 remove_previous: bool = True  # this will soften the memory requirement of the network
                 ):
        if to_ignore is None:
            to_ignore = []
        self.function: FUNCTION = function
        self.input_cls: Type[INPUT] = input_cls
        self.output_cls: Type[OUTPUT] = output_cls

        self.terminals: List[Element] = []

        self.terminal_ends: Set[POSITION] = set()
        self.non_terminal_ends: Dict[POSITION, OUTPUT_LAYER] = {}

        self.source: Optional[Iterator[INPUT]] = None

        self.pr: PositionRegister = PositionRegister()
        self.to_ignore: List[T_STATE] = to_ignore

        self.save_terminals: bool = save_terminals
        self.remove_previous: bool = remove_previous
        self.allow_gaps: bool = allow_gaps

    def feed_iterator(self, iterator: Iterator[INPUT]):
        """Give the Network a source of input items"""
        self.source = iterator

    def feed_network(self, network):
        """Give the Network a source using another network"""
        assert isinstance(network, Network)
        self.pr = network.pr
        self.feed_iterator(iter(network))

    def feed(self, obj):
        """Give the Network a source using either an Iterator of inputes or another Network"""
        if isinstance(obj, Network):
            return self.feed_network(obj)
        else:
            return self.feed_iterator(obj)

    def generate_from(self, o: OUTPUT, i: INPUT) -> Iterator[OUTPUT]:
        """Return the new outputs generated from the ``origin`` output and a ``target`` input"""
        for action, value in self.function(o.value, i):
            yield o.develop(action, value, i)

    def confirm_non_terminals(self, non_terminals: SetList[OUTPUT]) -> None:
        for o in non_terminals:
            self.add_non_terminal(o)

    def add_bridges(self, outputs: SetList[OUTPUT]) -> None:
        """Use the ``outputs`` to make bridges"""
        for o in outputs:
            a: POSITION = self.pr.get(o.start)
            b: POSITION = self.pr.get(o.end)
            self.merge_positions(a, b)

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

        for o in result:
            self.add_terminal(o)

        return result

    def add_terminal(self, o: OUTPUT) -> None:
        self.terminal_ends.add(self.pr.get(o.end))
        if self.save_terminals:
            self.terminals.append(o)

    def add_non_terminal(self, o: OUTPUT) -> None:
        p = self.pr.get(o.end)
        self.non_terminal_ends.setdefault(p, [])
        self.non_terminal_ends[p].append(o)

    def merge_positions(self, a: POSITION, b: POSITION):
        old, new = self.pr.merge(a, b)
        self.non_terminal_ends.setdefault(new, [])
        self.non_terminal_ends[new].extend(self.non_terminal_ends.pop(old, []))

    def elements_before(self, i: INPUT) -> OUTPUT_LAYER:
        """Yields the non-terminal elements that ends where ``i`` starts"""
        p = self.pr.get(i.start)
        return self.non_terminal_ends.get(p, [])

    def new_cursor(self, index: INDEX) -> None:
        """Create a new empty non-terminal element at ``index``"""
        p = self.pr.get(index)
        o = self.output_cls(start=index, end=index, value=0)
        self.non_terminal_ends.setdefault(p, [])
        self.non_terminal_ends[p].append(o)

    def can_continue_from(self, i: INPUT) -> bool:
        """Return True if any non-terminal element ends where ``i`` starts"""
        return self.pr.get(i.start) in self.non_terminal_ends

    def can_start_with(self, i: INPUT) -> bool:
        """Return True if any terminal element ends where ``i`` starts"""
        return i.start == 0 or self.pr.get(i.start) in self.terminal_ends

    def remove_before(self, i: INPUT) -> None:
        if self.remove_previous:
            p = self.pr.get(i.start)
            for r in [p_ for p_ in self.non_terminal_ends.keys() if p_ < p]:
                del self.non_terminal_ends[r]

            for r in [p_ for p_ in self.terminal_ends if p_ < p]:
                self.terminal_ends.remove(r)

    def gen(self, i: INPUT) -> OUTPUT_LAYER:
        """Generate bridge, non-terminal and terminal elements from the input ``i``"""
        non_terminals: SetList[OUTPUT] = SetList()
        bridges: SetList[OUTPUT] = SetList()
        terminals: SetList[OUTPUT] = SetList()

        self.remove_before(i)

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

    def terminal_table(self, **config):
        assert self.save_terminals
        return ReprTable.from_items(
            items=self.terminals,
            config={
                "start": lambda o: str(self.pr.get(o.start)),
                "end": lambda o: str(self.pr.get(o.end)),
                "value": lambda o: str(o.value),
                **config
            }
        )

    @property
    def non_terminals(self) -> List[OUTPUT]:
        return [
            nt
            for nts in self.non_terminal_ends.values()
            for nt in nts
        ]

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

    def __iter__(self) -> Generator[OUTPUT, None, None]:
        """Yields all the terminal elements that can be generated from the ``source``"""
        assert self.source is not None
        end = 0
        for input_element in self.source:
            yield from self.append(input_element)
            end = input_element.end
        yield from self.append(self.input_cls.EOF(end))

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

    def append(self, i: INPUT) -> OUTPUT_LAYER:
        """
            Return all the terminal elements generated considering the input ``i``
        """
        assert i.is_terminal

        if self.on(i):
            return self.gen(i)
        else:
            return []
