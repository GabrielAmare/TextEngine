from tkinter import *

# dict(identifier="MS_PART", mode="str", expr="∂", priority=SYMBOLS),
# dict(identifier="MS_NABLA", mode="str", expr="∇", priority=SYMBOLS),
# dict(identifier="MS_NI", mode="str", expr="∋", priority=SYMBOLS),
#
# dict(identifier="MS_MINUS", mode="str", expr="−", priority=SYMBOLS),
# dict(identifier="MS_LOWAST", mode="str", expr="∗", priority=SYMBOLS),
# dict(identifier="MS_RADIC", mode="str", expr="√", priority=SYMBOLS),
#
# dict(identifier="MS_ANG", mode="str", expr="∠", priority=SYMBOLS),
# dict(identifier="MS_INT", mode="str", expr="∫", priority=SYMBOLS),
# dict(identifier="MS_THERE4", mode="str", expr="∴", priority=SYMBOLS),
#
# dict(identifier="MS_CONG", mode="str", expr="≅", priority=SYMBOLS),
#
# dict(identifier="MS_NSUB", mode="str", expr="⊄", priority=SYMBOLS),
#
# dict(identifier="MS_SDOT", mode="str", expr="⋅", priority=SYMBOLS),


class TextMaths(Text):
    CHARMAP = {
        # https://unicode-table.com/fr/#229D
        'less': '≤',
        'greater': '≥',

        'ampersand': '∧',
        # '|': '∨',

        'a': '∀',
        'z': '∃',  # ∄
        'e': '⊂',
        'r': '⊃',
        't': '⊆',
        'y': '⊇',
        'u': '∈',
        'i': '∉',
        'o': '∅',
        'p': 'Ω',

        'q': '∏',
        's': '∑',
        'd': '∝',
        'f': '∞',
        'g': '∩',
        'h': '∪',
        'j': '≡',
        'k': '≈',
        'l': '≠',
        'm': '∼',

        'w': '⊕',  # ⊕ ⊖ ⊗ ⊘ ⊘ ⊚ ⊛ ⊜ ⊝
        'x': '⊗',
        'c': '⊥',
        'v': '◊',  # POSSIBILITY
        'b': '∎',  #
        'n': '¬',
        # INDICES
        '0': '₀',
        '1': '₁',
        '2': '₂',
        '3': '₃',
        '4': '₄',
        '5': '₅',
        '6': '₆',
        '7': '₇',
        '8': '₈',
        '9': '₉',
    }

    def __init__(self, root, **cfg):
        super().__init__(root, **cfg)

        for old, new in self.CHARMAP.items():
            self.bind_char(old, new)

        self.special_chars = False
        self.bind("<KeyPress-Alt_L>", lambda _: setattr(self, "special_chars", True))
        self.bind("<KeyRelease-Alt_L>", lambda _: setattr(self, "special_chars", False))

        self.bind("<Any-KeyPress>", lambda e: print(e))
        self.bind("<Any-KeyRelease>", lambda e: print(e))

    def bind_char(self, old: str, new: str):
        self.bind(f"<KeyPress-{old}>", lambda _: self.add(new))

    def add(self, char: str):
        if self.special_chars:
            self.insert(INSERT, char)


class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("Maths Text Handler")
        self.geometry("800x600")

        self.widget = TextMaths(self,
                                background="black",
                                foreground="white",
                                insertbackground="yellow",
                                font=("Consolas", 14)
                                )
        self.widget.pack(side=TOP, fill=BOTH, expand=True)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
