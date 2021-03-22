from tklib37 import *
from typing import List

from ..base import Result, Result_Unit, Result_List, Result_Error
from ..core.results import *


class Display_BuilderResult(Frame):
    CFG = dict(bg="black", fg="yellow", bd=2, relief=RAISED, font=("Consolas", 13), padx=10, pady=4)

    def __init__(self, root, result: BuilderResult, options=None, **config):
        super().__init__(root, bg="black", **config)
        self.head = Label(self, text=result.rule.name, **self.CFG, anchor=S)
        self.head.pack(side=TOP, fill=BOTH, expand=True)

        self.body = DisplayResult(self, result.result, options=options)
        if self.body:
            self.body.pack(side=BOTTOM, fill=X)


class Display_AsResult(Frame):
    CFG = dict(bg="black", fg="green", bd=0, relief=RIDGE, font=("Consolas", 11), padx=10, pady=4)

    def __init__(self, root, result: AsResult, options=None, **config):
        super().__init__(root, bg="black", **config)

        self.body = DisplayResult(self, result.result, options=options)
        self.body.pack(side=BOTTOM, fill=X)

        if not options.get("no_keys"):
            self.head = Label(self, text="↑ " + result.rule.key, **self.CFG)
            self.head.pack(side=BOTTOM, fill=X)


class Display_InResult(Frame):
    CFG = dict(bg="black", fg="green", bd=0, relief=RIDGE, font=("Consolas", 11), padx=10, pady=4)

    def __init__(self, root, result: InResult, options=None, **config):
        super().__init__(root, bg="black", **config)

        self.body = DisplayResult(self, result.result, options=options)
        self.body.pack(side=BOTTOM, fill=X)

        if not options.get("no_keys"):
            self.head = Label(self, text="↑ " + result.rule.key + "[]", **self.CFG)
            self.head.pack(side=BOTTOM, fill=X)


class Display_MatchResult(Frame):
    CFG_HEAD = dict(bg="black", fg="blue", bd=2, relief=SUNKEN, font=("Consolas", 12, "bold"), padx=5, pady=5)
    CFG_BODY = dict(bg="black", fg="gray", font=("Consolas", 11), padx=10, pady=4)

    def __init__(self, root, result: MatchResult, options=None, **config):
        super().__init__(root, bg="black", **config)

        self.head = Label(self, text=result.token.pattern.name, **self.CFG_HEAD)
        self.body = Label(self, text=repr(result.token.content)[1:-1], **self.CFG_BODY)

        self.body.pack(side=BOTTOM, fill=X)
        self.head.pack(side=BOTTOM, fill=X)


class Display_Result_Error(Frame):
    CFG_HEAD = dict(bg="black", fg="red", bd=2, relief=SUNKEN, font=("Consolas", 12, "bold"), padx=5, pady=5)
    CFG_BODY = dict(bg="black", fg="gray", font=("Consolas", 11), padx=10, pady=4)

    def __init__(self, root, result: Result_Error, options=None, **config):
        super().__init__(root, bg="black", **config)
        if result.result is not None:
            self.body = DisplayResult(self, result.result, options=options)
            self.body.pack(side=BOTTOM, fill=X)

        self.head = Label(self, text=result.reason, **self.CFG_HEAD)
        self.head.pack(side=BOTTOM, fill=X)


class Display_ResultsRow(Frame):
    def __init__(self, root, results: List[Result], options=None, **config):
        super().__init__(root, bg="black", **config)

        self.widgets = []
        for result in results:
            widget = DisplayResult(self, result, options=options)
            if options.get("no_unused_matches"):
                if isinstance(widget, Display_MatchResult):
                    continue

            if widget:
                print(type(widget))
                widget.pack(side=LEFT, fill=BOTH, expand=True)
                self.widgets.append(widget)



def DisplayResult(root, result, options=None, **config):
    if isinstance(result, BuilderResult):
        return Display_BuilderResult(root, result, options=options, **config)
    elif isinstance(result, AsResult):
        return Display_AsResult(root, result, options=options, **config)
    elif isinstance(result, InResult):
        return Display_InResult(root, result, options=options, **config)
    elif isinstance(result, MatchResult):
        return Display_MatchResult(root, result, options=options, **config)
    elif isinstance(result, Result_Error):
        return Display_Result_Error(root, result, options=options, **config)
    elif isinstance(result, Result_Unit):
        return DisplayResult(root, result.result, options=options, **config)
    elif isinstance(result, Result_List):
        d = Display_ResultsRow(root, result.results, options=options, **config)
        if len(d.widgets):
            return d
    else:
        raise Exception(type(result))


def display(*results, **options):
    """

    :param results:
    :param options: 'no_keys', 'no_unused_matches'
    :return:
    """
    tk = Tk()
    tk.configure(bg="black")
    ysf = YScrollFrame(tk, bg="black")
    ysf.pack(side=TOP, fill=BOTH, expand=True)
    ysf.set_widget(Frame, bg="black")

    for result in results:
        DisplayResult(ysf.widget, result, options=options, bd=2, relief=SUNKEN, padx=10, pady=10).pack(side=TOP, fill=X, padx=10, pady=10)

    tk.geometry(f"1200x600")

    tk.mainloop()
