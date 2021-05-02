from graph37 import *

STYLES = {
    # NODES
    "TEXT": dict(shape="box", style="filled", fillcolor="lightblue", color="black"),
    "START": dict(shape="box", style="filled", fillcolor="lime"),
    "END": dict(shape="box", style="filled", fillcolor="red"),
    # LINKS
    "LINK": dict(constraint="true", arrowhead="vee", arrowtail="none")
}


class DAG(DAG):

    def start(self, index: int):
        return self.node(type="start", label=f"START\n{index}", style=STYLES["START"])

    def end(self, index: int):
        return self.node(type="end", label=f"END\n{index}", style=STYLES["END"])

    def text(self, text):
        return self.node(type="text", label=text, style=STYLES["TEXT"])

    def link(self, origin, target, **config):
        return super().link(origin, target, style=STYLES["LINK"], **config)

    def chain(self, *elements):
        return [
            self.link(origin, target)
            for origin, target in zip(elements, elements[1:])
        ]
