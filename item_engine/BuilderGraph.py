from .items import Group
from graph37 import DAG
from .constants import NT_STATE, T_STATE, ACTION

__all__ = ["BuilderGraph"]


class STYLES:
    class NODES:
        class STATES:
            NON_TERMINAL = dict(shape="box", style="filled", fillcolor="lightblue", color="black")
            TERMINAL_VALID = dict(shape="box", style="filled", fillcolor="lime", color="black")
            TERMINAL_ERROR = dict(shape="box", style="filled", fillcolor="red", color="black")

        ACTION = dict(shape="box", style="filled", fillcolor="gray", color="black")
        GROUP = dict(shape="box", style="filled", fillcolor="gold", color="black")

        GROUP_ACTION = dict(shape="record", style="filled", fillcolor="gold", color="black")

    class LINKS:
        BASE = dict(constraint="true", arrowhead="vee", arrowtail="none")


class BuilderGraph(DAG):
    def non_terminal_state(self, value: NT_STATE):
        return self.node(
            type="non_terminal_state",
            label=str(value),
            style=STYLES.NODES.STATES.NON_TERMINAL
        )

    def terminal_error_state(self, value: T_STATE):
        return self.node(
            type="terminal_error_state",
            label='\n'.join(map(repr, sorted(value[1:].split('|')))),
            style=STYLES.NODES.STATES.TERMINAL_ERROR
        )

    def terminal_valid_state(self, value: T_STATE):
        return self.node(
            type="terminal_valid_state",
            label='\n'.join(map(repr, sorted(value.split('|')))),
            style=STYLES.NODES.STATES.TERMINAL_VALID
        )

    def action(self, action: ACTION):
        return self.node(
            type="action",
            label=action,
            style=STYLES.NODES.ACTION
        )

    def group(self, group: Group):
        return self.node(
            type="group",
            label=str(group),
            style=STYLES.NODES.GROUP
        )

    def link(self, origin, target, **config):
        return super().link(origin, target, style=STYLES.LINKS.BASE, **config)

    def group_action(self, group: Group, action: ACTION):
        gs = '{' + str(group).replace('|', '\\|').replace('\n', '|') + '}'
        return self.node(
            label=f"{gs}|{action!s}",
            style=STYLES.NODES.GROUP_ACTION
        )

    def chain(self, *elements):
        return [
            self.link(origin, target)
            for origin, target in zip(elements, elements[1:])
        ]

    def display(self, splines="ortho", ranksep=0.5, view: bool = True):
        import graphviz as gv

        import os
        os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz-2.38/bin/'

        dot = gv.Digraph(
            format="svg",
            engine="dot",
            graph_attr=dict(
                ranksep=str(ranksep),
                color='white',
                splines='ortho'
            )
        )

        for node in self.nodes:
            dot.node(
                name=str(id(node)),
                label=node.get("label", ""),
                **node.get("style", {})
            )

        for link in self.links:
            dot.edge(
                tail_name=str(id(link.origin)),
                head_name=str(id(link.target)),
                **link.get("style", {})
            )
        directory, filename = os.path.split(self.get("name", "digraph"))
        if view:
            dot.view(filename=filename)
        else:
            directory, filename = os.path.split(self.get("name", "digraph"))
            dot.render(cleanup=True, filename=filename, directory=directory, quiet=True)
