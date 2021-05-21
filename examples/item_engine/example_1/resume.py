import os
from timeit import timeit


def resume_package(package_path: str):
    """This function will print a resume of the specified package"""
    assert os.path.exists(package_path)

    for filename in os.listdir(package_path):
        filepath = os.path.join(package_path, filename).replace('\\', '/')
        try:
            with open(filepath, mode="r", encoding="utf-8") as file:
                length = len(file.read().split('\n'))
                print(f"{filepath!r} : {length!r} lines")
        except PermissionError:
            continue


def main():
    from examples.item_engine.example_1.define import engine

    d = timeit(lambda: engine.build(allow_overwrite=True), number=1)

    print(f"generation took {int(d * 1e3)} ms")

    # SHOW LENGTH OF THE GENERATED FILES
    resume_package("maths")


if __name__ == '__main__':
    main()
