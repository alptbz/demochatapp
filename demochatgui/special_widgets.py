from tkinter import Text
from idlelib.redirector  import WidgetRedirector
from tkinter.scrolledtext import ScrolledText


class ReadOnlyText(ScrolledText):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")
