from item_engine.textbase import *


def build(e: Element):
    if isinstance(e, Lemma):
        pass
    elif isinstance(e, Token):
        pass
    else:
        raise Exception(e.value)
