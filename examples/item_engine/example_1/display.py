from examples.item_engine.example_1.define import engine

engine.build(allow_overwrite=True)

for parser in engine.parsers:
    parser.graph.display()

# print(engine.data().code())
