import os
import tkinter as tk
from tkinter import messagebox
from typing import Callable

import pyautogui

from src.constant import CAPTURE_SCREEN_RECT_MIN_LENGTH, TEMP_FILE_NAME
from src.gui_constant import (
    SCREEN_CAPTURE_CANCEL_DELAY,
    SCREEN_CAPTURE_WARNING_MESSAGE,
    SCREEN_CAPTURE_WARNING_TITLE,
)


class CaptureScreen(tk.Toplevel):
    def __init__(
        self,
        root: tk.Tk,
        image_path_var: tk.StringVar,
        status_var: tk.StringVar,
        recognize_digits: Callable[[], None],
    ):
        super().__init__(root)
        self.root = root
        self.attributes("-fullscreen", True)  # pyright: ignore[reportUnknownMemberType]
        self.attributes("-alpha", 0.3)  # pyright: ignore[reportUnknownMemberType]
        self.attributes("-topmost", True)  # pyright: ignore[reportUnknownMemberType]
        self.config(cursor="cross")
        self.image_path_var = image_path_var
        self.status_var = status_var
        self.recognize_digits = recognize_digits

    def create_canvas(self, screen_width: int, screen_height: int):
        canvas = tk.Canvas(self, width=screen_width, height=screen_height)
        canvas.pack(fill=tk.BOTH, expand=True)
        return canvas

    def handle_select_region_events(self, canvas: tk.Canvas):
        start_x = None
        start_y = None
        rect = None

        def on_mouse_down(event: tk.Event):
            nonlocal start_x, start_y, rect
            start_x = event.x_root
            start_y = event.y_root
            if rect:
                canvas.delete(rect)
            rect = canvas.create_rectangle(
                start_x, start_y, start_x, start_y, outline="red", width=2
            )

        def on_mouse_move(event: tk.Event):
            nonlocal rect
            if start_x is not None and start_y is not None:
                current_x = event.x_root
                current_y = event.y_root
                assert (
                    rect is not None
                ), "rect must be initialized before calling on_mouse_move"
                canvas.coords(rect, start_x, start_y, current_x, current_y)

        def on_mouse_up(event: tk.Event):
            nonlocal start_x, start_y
            if start_x is not None and start_y is not None:
                end_x = event.x_root
                end_y = event.y_root
                x1 = min(start_x, end_x)
                y1 = min(start_y, end_y)
                x2 = max(start_x, end_x)
                y2 = max(start_y, end_y)
                if (
                    x2 - x1 > CAPTURE_SCREEN_RECT_MIN_LENGTH
                    and y2 - y1 > CAPTURE_SCREEN_RECT_MIN_LENGTH
                ):
                    self.destroy()
                    self.capture_selected_region(x1, y1, x2, y2)
                else:
                    self.destroy()
                    self.root.deiconify()
                    messagebox.showinfo(
                        SCREEN_CAPTURE_WARNING_TITLE,
                        SCREEN_CAPTURE_WARNING_MESSAGE,
                    )
                start_x = None
                start_y = None

        canvas.bind("<Button-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_move)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)

        def on_right_click(event: tk.Event):
            def cancel_after_delay():
                self.destroy()
                self.root.deiconify()

            self.after(SCREEN_CAPTURE_CANCEL_DELAY, cancel_after_delay)

        canvas.bind("<Button-3>", on_right_click)

    def capture_selected_region(self, x1: int, y1: int, x2: int, y2: int):
        try:
            screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
            temp_file = os.path.join(os.path.abspath("."), TEMP_FILE_NAME)
            screenshot.save(temp_file)
            self.root.deiconify()
            self.image_path_var.set(temp_file)
            self.status_var.set(
                f"已截取屏幕区域，保存为: {os.path.basename(temp_file)}"
            )
            self.recognize_digits()
        except Exception as e:
            messagebox.showerror("错误", f"截取屏幕失败: {str(e)}")
            self.status_var.set(f"截取屏幕失败: {str(e)}")
