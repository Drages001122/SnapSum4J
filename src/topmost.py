import tkinter as tk

from src.gui_constant import (
    TOPMOST_DISABLE_MESSAGE,
    TOPMOST_ENABLE_MESSAGE,
    TOPMOST_PADY,
    TOPMOST_TEXT,
)


class TopmostButton(tk.Checkbutton):
    def __init__(
        self,
        root: tk.Tk,
        parent: tk.Frame,
        topmost_var: tk.BooleanVar,
        status_var: tk.StringVar,
    ):
        super().__init__(
            parent, text=TOPMOST_TEXT, variable=topmost_var, command=self.toggle_topmost
        )
        self.pack(anchor=tk.W, pady=TOPMOST_PADY)
        self.root = root
        self.topmost_var = topmost_var
        self.status_var = status_var

    def enable_topmost(self, enabled: bool):
        self.root.attributes(  # pyright: ignore[reportUnknownMemberType]
            "-topmost", enabled
        )

    def toggle_topmost(self):
        is_topmost = self.topmost_var.get()
        self.enable_topmost(is_topmost)
        if is_topmost:
            self.status_var.set(TOPMOST_ENABLE_MESSAGE)
        else:
            self.status_var.set(TOPMOST_DISABLE_MESSAGE)
